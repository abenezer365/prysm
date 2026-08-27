"""Report generators — generation, realism, and validation reports."""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl

from src.utils.io import write_json_report


def build_generation_report(
    datasets: dict[str, pl.DataFrame],
    config: dict,
    seed: int,
    runtime_seconds: float,
    output_dir: Path,
) -> dict[str, Any]:
    counts = {name: len(df) for name, df in datasets.items()}
    total = sum(counts.values())
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "seed": seed,
        "runtime_seconds": round(runtime_seconds, 2),
        "total_records": total,
        "dataset_counts": counts,
        "config": {
            "temporal": config.get("temporal"),
            "output": config.get("output"),
            "data_quality": config.get("data_quality"),
        },
    }
    write_json_report(report, output_dir / "generation_report.json")
    return report


def build_realism_report(
    datasets: dict[str, pl.DataFrame],
    config: dict,
    output_dir: Path,
) -> dict[str, Any]:
    persons = datasets.get("persons")
    transactions = datasets.get("transactions")
    relationships = datasets.get("relationships")

    eth_ratio = None
    gender_dist = None
    city_dist = None
    income_stats = None
    if persons is not None:
        eth_ratio = round(
            len(persons.filter(pl.col("nationality") == "Ethiopian")) / max(1, len(persons)), 4
        )
        gender_dist = persons.group_by("gender").agg(pl.len().alias("count")).to_dicts()
        city_dist = (
            persons.group_by("city")
            .agg(pl.len().alias("count"))
            .sort("count", descending=True)
            .head(10)
            .to_dicts()
        )
        income_stats = {
            "mean": round(persons["declared_monthly_income"].mean(), 2),
            "median": round(persons["declared_monthly_income"].median(), 2),
            "min": int(persons["declared_monthly_income"].min()),
            "max": int(persons["declared_monthly_income"].max()),
        }

    tx_currency_dist = None
    if transactions is not None:
        tx_currency_dist = (
            transactions.group_by("currency")
            .agg(pl.len().alias("count"))
            .to_dicts()
        )

    rel_type_dist = None
    if relationships is not None:
        rel_type_dist = (
            relationships.group_by("relationship_type")
            .agg(pl.len().alias("count"))
            .to_dicts()
        )

    report = {
        "ethiopian_nationality_ratio": eth_ratio,
        "gender_distribution": gender_dist,
        "top_10_cities_by_population": city_dist,
        "income_statistics_etb": income_stats,
        "transaction_currency_distribution": tx_currency_dist,
        "relationship_type_distribution": rel_type_dist,
    }
    write_json_report(report, output_dir / "realism_report.json")
    return report


def build_validation_report(
    datasets: dict[str, pl.DataFrame],
    integrity_result: dict[str, Any],
    config: dict,
    output_dir: Path,
) -> dict[str, Any]:
    dq_cfg = config.get("data_quality", {})
    col_rates = dq_cfg.get("column_missing_rates", {})

    missing_stats: dict[str, Any] = {}
    for ds_name, df in datasets.items():
        ds_missing: dict[str, float] = {}
        for col in df.columns:
            null_count = df[col].null_count()
            if null_count > 0:
                ds_missing[col] = round(null_count / max(1, len(df)), 4)
        if ds_missing:
            missing_stats[ds_name] = ds_missing

    report = {
        "integrity": integrity_result,
        "missing_value_rates": missing_stats,
        "configured_missing_rates": col_rates,
        "duplicate_rate_configured": dq_cfg.get("duplicate_rate", 0.01),
        "schema_columns": {
            name: df.columns for name, df in datasets.items()
        },
    }
    write_json_report(report, output_dir / "validation_report.json")
    return report
