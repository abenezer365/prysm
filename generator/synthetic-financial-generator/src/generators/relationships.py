"""Relationships generator — 500,000 entity-level relationship edges."""
from __future__ import annotations

from datetime import datetime

import numpy as np
import polars as pl


def generate_relationships(
    config: dict,
    person_ids: list[str],
    company_ids: list[str],
    account_ids: list[str],
) -> pl.DataFrame:
    seed: int = config.get("seed", 42) + 6
    count: int = config.get("dataset", {}).get("relationships", 500_000)
    ref_date: str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    start_date: str = config.get("temporal", {}).get("start_date", "2022-01-01")
    ref_ts = datetime.fromisoformat(ref_date).timestamp()
    start_ts = datetime.fromisoformat(start_date).timestamp()

    rng = np.random.default_rng(seed)
    rel_types = config.get("relationship_types", [
        "family", "business_partner", "shared_device", "shared_address",
        "employer_employee", "guarantor", "joint_account", "counterpart",
        "supplier_customer", "referral",
    ])
    rel_weights = [0.15, 0.12, 0.10, 0.10, 0.12, 0.08, 0.08, 0.10, 0.10, 0.05]
    rel_weights = [w / sum(rel_weights) for w in rel_weights]

    all_entity_ids = person_ids + company_ids + account_ids
    all_entity_types = (
        ["Person"] * len(person_ids)
        + ["Company"] * len(company_ids)
        + ["Account"] * len(account_ids)
    )

    relationships: list[dict] = []
    for i in range(count):
        src_idx = rng.integers(0, len(all_entity_ids))
        tgt_idx = rng.integers(0, len(all_entity_ids))
        if tgt_idx == src_idx:
            tgt_idx = (tgt_idx + 1) % len(all_entity_ids)

        rel_type = rel_types[rng.choice(len(rel_types), p=rel_weights)]
        start_time_ts = rng.uniform(start_ts, ref_ts)
        end_time_ts = None
        if rng.random() < 0.25:
            end_time_ts = rng.uniform(start_time_ts, ref_ts)

        confidence = round(float(rng.uniform(0.3, 1.0)), 4)

        relationships.append(
            {
                "relationship_id": f"REL{str(i + 1).zfill(7)}",
                "source_type": all_entity_types[src_idx],
                "source_id": all_entity_ids[src_idx],
                "relationship_type": rel_type,
                "target_type": all_entity_types[tgt_idx],
                "target_id": all_entity_ids[tgt_idx],
                "start_time": datetime.fromtimestamp(start_time_ts),
                "end_time": datetime.fromtimestamp(end_time_ts) if end_time_ts else None,
                "confidence": confidence,
            }
        )

    return pl.DataFrame(relationships)
