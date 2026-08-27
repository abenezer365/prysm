"""Ground truth generator — 5,000 ML-labelled anomaly records."""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import polars as pl


def generate_ground_truth(
    config: dict,
    person_ids: list[str],
    company_ids: list[str],
    account_ids: list[str],
    transaction_ids: list[str],
) -> pl.DataFrame:
    seed: int = config.get("seed", 42) + 7
    count: int = config.get("dataset", {}).get("ground_truth", 5_000)
    ref_date: str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    start_date: str = config.get("temporal", {}).get("start_date", "2022-01-01")
    ref_dt = datetime.fromisoformat(ref_date)
    start_dt = datetime.fromisoformat(start_date)
    total_days = (ref_dt - start_dt).days

    rng = np.random.default_rng(seed)
    behavior_types = config.get("behavior_types", [
        "smurfing", "layering", "round_tripping", "structuring",
        "rapid_movement", "shell_company", "false_invoice", "normal",
    ])
    # 80% anomalous behaviors, 20% normal (label imbalance)
    beh_weights = [0.12, 0.12, 0.10, 0.12, 0.10, 0.10, 0.10, 0.24]
    beh_weights = [w / sum(beh_weights) for w in beh_weights]

    risk_patterns = config.get("risk_patterns", [
        "AML_HIGH", "AML_MEDIUM", "AML_LOW", "FRAUD_HIGH", "FRAUD_MEDIUM", "NORMAL",
    ])
    severity_levels = config.get("severity_levels", ["critical", "high", "medium", "low", "info"])

    all_entity_ids = person_ids + company_ids + account_ids
    all_entity_types = (
        ["Person"] * len(person_ids)
        + ["Company"] * len(company_ids)
        + ["Account"] * len(account_ids)
    )

    records: list[dict] = []
    for i in range(count):
        entity_idx = rng.integers(0, len(all_entity_ids))
        beh = behavior_types[rng.choice(len(behavior_types), p=beh_weights)]
        is_anomalous = beh != "normal"

        if is_anomalous:
            risk = rng.choice(risk_patterns[:-1])  # exclude NORMAL
            severity = rng.choice(severity_levels[:-1])  # exclude info
        else:
            risk = "NORMAL"
            severity = "info"

        pattern_start = (start_dt + timedelta(days=int(rng.integers(0, total_days)))).date()
        pattern_end = None
        if rng.random() < 0.60:
            days_span = int(rng.integers(7, 180))
            end_dt = datetime.combine(pattern_start, datetime.min.time()) + timedelta(days=days_span)
            pattern_end = min(end_dt, ref_dt).date()

        # Related entities: 2–8 transaction IDs or other entity IDs
        n_related = int(rng.integers(2, 9))
        related_pool = transaction_ids[:10_000] + all_entity_ids[:5_000]
        related_ids = [
            related_pool[rng.integers(0, len(related_pool))]
            for _ in range(n_related)
        ]

        records.append(
            {
                "ground_truth_id": f"GT{str(i + 1).zfill(5)}",
                "entity_type": all_entity_types[entity_idx],
                "entity_id": all_entity_ids[entity_idx],
                "behavior_type": beh,
                "risk_pattern": risk,
                "is_anomalous": is_anomalous,
                "severity": severity,
                "pattern_start": pattern_start,
                "pattern_end": pattern_end,
                "related_entity_ids": related_ids,
            }
        )

    return pl.DataFrame(records)
