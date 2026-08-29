from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

import polars as pl
import pytest


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SOURCE = REPO / "generator" / "synthetic-financial-generator" / "data" / "raw"
OUTPUT = ROOT / "output"
SPEC = importlib.util.spec_from_file_location("generate_scenarios", ROOT / "generate_scenarios.py")
assert SPEC and SPEC.loader
scenario_gen = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = scenario_gen
SPEC.loader.exec_module(scenario_gen)


@pytest.fixture(scope="module")
def artifacts():
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    sources = {
        "source_transactions": pl.read_parquet(SOURCE / "transactions.parquet"),
        "source_ground_truth": pl.read_parquet(SOURCE / "ground_truth.parquet"),
        "accounts": pl.read_parquet(SOURCE / "accounts.parquet"),
    }
    transactions = pl.read_parquet(OUTPUT / "data" / "transactions.parquet")
    ground_truth = pl.read_parquet(OUTPUT / "data" / "ground_truth.parquet")
    metadata = pl.read_parquet(OUTPUT / "scenario_metadata.parquet")
    return config, sources, transactions, ground_truth, metadata


def test_complete_standalone_dataset_exists():
    expected = {
        "persons.parquet", "companies.parquet", "accounts.parquet", "banks.parquet",
        "devices.parquet", "invoices.parquet", "relationships.parquet",
        "transactions.parquet", "ground_truth.parquet",
    }
    assert {path.name for path in (OUTPUT / "data").glob("*.parquet")} == expected


def test_existing_schemas_are_preserved(artifacts):
    _, sources, transactions, ground_truth, _ = artifacts
    assert transactions.schema == sources["source_transactions"].schema
    assert ground_truth.schema == sources["source_ground_truth"].schema


def test_original_transactions_are_unchanged_prefix(artifacts):
    _, sources, transactions, _, _ = artifacts
    source = sources["source_transactions"]
    assert transactions.head(source.height).equals(source)
    assert transactions["transaction_id"].n_unique() == transactions.height


def test_entity_account_transaction_affiliation_and_timing(artifacts):
    _, sources, transactions, ground_truth, metadata = artifacts
    evidence = (
        ground_truth.select("ground_truth_id", "pattern_start", "pattern_end", "related_entity_ids")
        .explode("related_entity_ids", empty_as_null=True)
        .join(metadata.select("ground_truth_id", "account_id", "prediction_cutoff"), on="ground_truth_id")
        .join(
            transactions.select("transaction_id", "timestamp", "sender_account_id", "receiver_account_id"),
            left_on="related_entity_ids",
            right_on="transaction_id",
            how="left",
        )
    )
    assert evidence["timestamp"].null_count() == 0
    assert evidence.filter(
        (pl.col("sender_account_id") != pl.col("account_id"))
        & (pl.col("receiver_account_id") != pl.col("account_id"))
    ).is_empty()
    assert evidence.filter(pl.col("timestamp") <= pl.col("prediction_cutoff")).is_empty()
    assert evidence.filter(
        pl.col("timestamp") > pl.col("pattern_end").cast(pl.Datetime) + pl.duration(days=1)
    ).is_empty()


def test_class_and_scenario_balance(artifacts):
    config, _, _, ground_truth, _ = artifacts
    assert ground_truth.filter(pl.col("is_anomalous")).height == 3500
    assert ground_truth.filter(~pl.col("is_anomalous")).height == 3500
    counts = dict(ground_truth.group_by("behavior_type").len().select("behavior_type", "len").iter_rows())
    assert counts["normal"] == 3500
    for scenario in config["scenarios"]:
        assert counts[scenario] == 500


def test_entity_disjoint_splits(artifacts):
    _, _, _, _, metadata = artifacts
    entities = {
        split: set(metadata.filter(pl.col("split") == split)["entity_key"].to_list())
        for split in ["train", "validation", "test"]
    }
    assert not entities["train"] & entities["validation"]
    assert not entities["train"] & entities["test"]
    assert not entities["validation"] & entities["test"]
    assert metadata["entity_key"].n_unique() == metadata.height


def test_every_observation_has_sufficient_pre_cutoff_history(artifacts):
    config, _, _, _, metadata = artifacts
    assert metadata["history_transaction_count"].min() >= config["minimum_history_transactions"]


def test_independent_behavior_and_readiness_validation(artifacts):
    config, sources, transactions, ground_truth, metadata = artifacts
    result = scenario_gen.validate_dataset(sources, transactions, ground_truth, metadata, config)
    assert result["validation"]["scenario_behavior_failures"] == 0
    assert result["validation"]["invalid_entity_affiliations"] == 0
    assert result["validation"]["invalid_transaction_affiliations"] == 0
    assert result["validation"]["fabricated_transaction_ids"] == 0
    assert result["validation"]["temporal_violations"] == 0
    assert result["model_readiness"]["status"] == "READY"


def test_deterministic_subject_activity():
    schema = pl.read_parquet_schema(SOURCE / "transactions.parquet")
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    subject = scenario_gen.Subject(
        "train", "Person", "P1", "A1", datetime(2024, 6, 1), True, "rapid_movement", "medium"
    )
    profile = {
        "history": [], "history_count": 8, "median_amount_etb": 10_000.0,
        "p90_amount_etb": 20_000.0, "foreign_share": 0.0,
        "counterparties": ["A2"], "device_id": "D1", "channel": "Mobile Banking", "currency": "ETB",
    }
    owners = {f"A{i}": f"Person:P{i}" for i in range(1, 30)}
    pool = sorted(owners)
    first = scenario_gen.TransactionFactory(700_000, schema, config["fx_rates_to_etb"])
    second = scenario_gen.TransactionFactory(700_000, schema, config["fx_rates_to_etb"])
    result_one = scenario_gen.generate_subject_activity(subject, profile, first, pool, set(pool), owners, ["D1", "D2"], config)
    result_two = scenario_gen.generate_subject_activity(subject, profile, second, pool, set(pool), owners, ["D1", "D2"], config)
    assert first.rows == second.rows
    assert result_one == result_two


def test_manifest_matches_every_output_file():
    manifest = json.loads((OUTPUT / "MANIFEST.json").read_text(encoding="utf-8"))
    for relative_path, details in manifest["files"].items():
        path = OUTPUT / relative_path
        assert path.exists()
        assert scenario_gen._sha256(path) == details["sha256"]


def test_original_source_files_are_not_inside_output_mutation_scope():
    manifest = json.loads((OUTPUT / "MANIFEST.json").read_text(encoding="utf-8"))
    for filename in scenario_gen.UNCHANGED_DATASETS:
        assert scenario_gen._sha256(SOURCE / filename) == manifest["files"][f"data/{filename}"]["sha256"]
