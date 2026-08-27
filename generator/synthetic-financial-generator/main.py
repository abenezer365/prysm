"""
main.py — CLI entry point for the Synthetic Ethiopian Financial Data Generator.

Usage:
    python main.py [OPTIONS]

Options:
    --seed INTEGER       Random seed for reproducibility (default: from config)
    --config PATH        Path to config.yaml (default: ./config.yaml)
    --output-dir PATH    Output directory for Parquet files (default: ./data/raw)
    --reports-dir PATH   Output directory for JSON reports (default: ./reports)
    --sample             Also write 1,000-row CSV samples to data/samples/
    --no-quality         Skip data-quality corruption step
    --no-validate        Skip post-generation validation

Example:
    python main.py --seed 42
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import click
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import polars as pl
import yaml

# Make src importable when running from generator root
_GENERATOR_ROOT = Path(__file__).resolve().parent
if str(_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(_GENERATOR_ROOT))

from src.generators.banks import generate_banks
from src.generators.persons import generate_persons
from src.generators.companies import generate_companies
from src.generators.accounts import generate_accounts
from src.generators.devices import generate_devices
from src.generators.invoices import generate_invoices
from src.generators.transactions import generate_transactions
from src.generators.relationships import generate_relationships
from src.generators.ground_truth import generate_ground_truth

from src.data_quality.missing_values import apply_missing_values
from src.data_quality.duplicates import inject_duplicates
from src.data_quality.corruption import apply_formatting_corruption

from src.validation.integrity import validate_all
from src.validation.reports import (
    build_generation_report,
    build_realism_report,
    build_validation_report,
)
from src.utils.io import write_parquet, write_csv_sample


# ---------------------------------------------------------------------------
# Parquet schema definitions with list<string> support
# ---------------------------------------------------------------------------

def _write_with_list_schema(df: pl.DataFrame, path: Path, compression: str, row_group_size: int) -> None:
    """Write a DataFrame that may contain list columns to Parquet via PyArrow."""
    path.parent.mkdir(parents=True, exist_ok=True)
    table = df.to_arrow()
    pq.write_table(table, str(path), compression=compression, row_group_size=row_group_size)


def _log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    # Replace any unicode arrows/checkmarks for Windows cp1252 compatibility
    msg = msg.replace("\u2192", "->").replace("\u2713", "[OK]").replace("\u2717", "[FAIL]")
    click.echo(f"[{ts}] {msg}")


@click.command()
@click.option("--seed", default=None, type=int, help="Random seed (overrides config)")
@click.option(
    "--config",
    "config_path",
    default="config.yaml",
    show_default=True,
    type=click.Path(exists=True),
    help="Path to config.yaml",
)
@click.option(
    "--output-dir",
    default="data/raw",
    show_default=True,
    help="Output directory for Parquet files",
)
@click.option(
    "--reports-dir",
    default="reports",
    show_default=True,
    help="Output directory for JSON reports",
)
@click.option("--sample", is_flag=True, default=False, help="Write 1k-row CSV samples")
@click.option("--no-quality", is_flag=True, default=False, help="Skip data-quality corruption")
@click.option("--no-validate", is_flag=True, default=False, help="Skip validation step")
def main(
    seed: int | None,
    config_path: str,
    output_dir: str,
    reports_dir: str,
    sample: bool,
    no_quality: bool,
    no_validate: bool,
) -> None:
    t_start = time.time()

    # ------------------------------------------------------------------
    # Load config
    # ------------------------------------------------------------------
    config_file = Path(config_path)
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if seed is not None:
        config["seed"] = seed
    effective_seed: int = config.get("seed", 42)
    np.random.seed(effective_seed)

    output_path = Path(output_dir)
    reports_path = Path(reports_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    reports_path.mkdir(parents=True, exist_ok=True)

    compression = config.get("output", {}).get("compression", "zstd")
    row_group_size = config.get("output", {}).get("row_group_size", 100_000)
    dq_cfg = config.get("data_quality", {})
    col_missing = dq_cfg.get("column_missing_rates", {})
    dup_rate = dq_cfg.get("duplicate_rate", 0.01)
    corruption_rate = 0.02  # 2% formatting corruption on string fields

    _log(f"Seed: {effective_seed} | Config: {config_file}")
    _log(f"Output: {output_path} | Reports: {reports_path}")

    rng_quality = np.random.default_rng(effective_seed + 99)

    # ------------------------------------------------------------------
    # 1. Banks (no dependencies)
    # ------------------------------------------------------------------
    _log("Generating banks …")
    banks_df = generate_banks(config)
    _log(f"  → {len(banks_df):,} banks")

    # ------------------------------------------------------------------
    # 2. Persons
    # ------------------------------------------------------------------
    _log("Generating persons …")
    persons_df = generate_persons(config)
    _log(f"  → {len(persons_df):,} persons")

    # ------------------------------------------------------------------
    # 3. Companies
    # ------------------------------------------------------------------
    _log("Generating companies …")
    companies_df = generate_companies(config)
    _log(f"  → {len(companies_df):,} companies")

    # Collect IDs for downstream generators
    person_ids: list[str] = persons_df["person_id"].to_list()
    company_ids: list[str] = companies_df["company_id"].to_list()
    bank_ids: list[str] = banks_df["institution_id"].to_list()

    # ------------------------------------------------------------------
    # 4. Accounts (depends on persons, companies, banks)
    # ------------------------------------------------------------------
    _log("Generating accounts …")
    accounts_df = generate_accounts(config, person_ids, company_ids, bank_ids)
    _log(f"  → {len(accounts_df):,} accounts")
    account_ids: list[str] = accounts_df["account_id"].to_list()

    # ------------------------------------------------------------------
    # 5. Devices
    # ------------------------------------------------------------------
    _log("Generating devices …")
    devices_df = generate_devices(config)
    _log(f"  → {len(devices_df):,} devices")
    device_ids: list[str] = devices_df["device_id"].to_list()

    # ------------------------------------------------------------------
    # 6. Invoices (depends on persons, companies)
    # ------------------------------------------------------------------
    _log("Generating invoices …")
    invoices_df = generate_invoices(config, person_ids, company_ids)
    _log(f"  → {len(invoices_df):,} invoices")
    invoice_ids: list[str] = invoices_df["invoice_id"].to_list()

    # ------------------------------------------------------------------
    # 7. Transactions (depends on accounts, devices, invoices)
    # ------------------------------------------------------------------
    _log("Generating transactions … (this is the largest dataset)")
    transactions_df = generate_transactions(config, account_ids, device_ids, invoice_ids)
    _log(f"  → {len(transactions_df):,} transactions")
    transaction_ids: list[str] = transactions_df["transaction_id"].to_list()

    # ------------------------------------------------------------------
    # 8. Relationships (depends on persons, companies, accounts)
    # ------------------------------------------------------------------
    _log("Generating relationships …")
    relationships_df = generate_relationships(config, person_ids, company_ids, account_ids)
    _log(f"  → {len(relationships_df):,} relationships")

    # ------------------------------------------------------------------
    # 9. Ground Truth (depends on all entity and transaction IDs)
    # ------------------------------------------------------------------
    _log("Generating ground truth …")
    ground_truth_df = generate_ground_truth(
        config, person_ids, company_ids, account_ids, transaction_ids
    )
    _log(f"  → {len(ground_truth_df):,} ground truth records")

    # ------------------------------------------------------------------
    # Collect all datasets
    # ------------------------------------------------------------------
    datasets: dict[str, pl.DataFrame] = {
        "persons": persons_df,
        "companies": companies_df,
        "banks": banks_df,
        "accounts": accounts_df,
        "devices": devices_df,
        "invoices": invoices_df,
        "transactions": transactions_df,
        "relationships": relationships_df,
        "ground_truth": ground_truth_df,
    }

    # ------------------------------------------------------------------
    # Data Quality Step
    # ------------------------------------------------------------------
    if not no_quality:
        _log("Applying data quality (missing values, duplicates, corruption) …")

        # Missing values — applied globally on relevant datasets
        missing_targets = {
            "persons": ["phone_hash", "address_hash", "employment_status"],
            "accounts": ["closed_at"],
            "devices": ["browser"],
            "transactions": ["device_id", "invoice_id", "ip_hash"],
        }
        for ds_name, cols in missing_targets.items():
            df = datasets[ds_name]
            rates = {c: col_missing.get(c, 0.05) for c in cols if c in df.columns}
            datasets[ds_name] = apply_missing_values(df, rates, rng_quality)

        # Near-duplicates on persons (most impactful for entity resolution)
        datasets["persons"] = inject_duplicates(
            datasets["persons"],
            duplicate_rate=dup_rate,
            rng=rng_quality,
            string_columns=["first_name", "last_name", "city"],
        )
        _log(f"  persons (with dupes): {len(datasets['persons']):,}")

        # Formatting corruption on persons and companies
        datasets["persons"] = apply_formatting_corruption(
            datasets["persons"], corruption_rate, rng_quality, ["first_name", "last_name"]
        )
        datasets["companies"] = apply_formatting_corruption(
            datasets["companies"], corruption_rate, rng_quality, ["company_name", "city"]
        )

    # ------------------------------------------------------------------
    # Write Parquet files
    # ------------------------------------------------------------------
    _log("Writing Parquet files …")
    for ds_name, df in datasets.items():
        out_file = output_path / f"{ds_name}.parquet"
        # Use PyArrow directly to preserve list<string> columns
        _write_with_list_schema(df, out_file, compression, row_group_size)
        _log(f"  ✓ {out_file.name} ({len(df):,} rows)")

    # ------------------------------------------------------------------
    # CSV Samples
    # ------------------------------------------------------------------
    if sample:
        _log("Writing CSV samples …")
        samples_path = Path("data/samples")
        for ds_name, df in datasets.items():
            write_csv_sample(df, samples_path / f"{ds_name}_sample.csv")
        _log(f"  ✓ CSV samples written to {samples_path}")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    integrity_result: dict = {"passed": True, "error_count": 0, "warning_count": 0, "errors": [], "warnings": []}
    if not no_validate:
        _log("Running integrity validation …")
        integrity_result = validate_all(datasets, config)
        status = "✓ PASSED" if integrity_result["passed"] else f"✗ FAILED ({integrity_result['error_count']} errors)"
        _log(f"  Validation: {status}")
        if integrity_result["errors"]:
            for err in integrity_result["errors"][:10]:
                _log(f"    ERROR: {err}")

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------
    _log("Writing JSON reports …")
    runtime = time.time() - t_start
    build_generation_report(datasets, config, effective_seed, runtime, reports_path)
    build_realism_report(datasets, config, reports_path)
    build_validation_report(datasets, integrity_result, config, reports_path)
    _log(f"  ✓ Reports written to {reports_path}/")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    total_records = sum(len(df) for df in datasets.values())
    _log("=" * 60)
    _log(f"DONE in {runtime:.1f}s — {total_records:,} total records generated")
    _log(f"Parquet files → {output_path.resolve()}")
    _log(f"Reports       → {reports_path.resolve()}")
    _log("=" * 60)


if __name__ == "__main__":
    main()
