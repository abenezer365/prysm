"""Audit label provenance and construct a defensible predictive population.

Source labels are immutable. This module adds derived eligibility/status fields;
it never changes ``is_anomalous`` or invents events.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_alignment_table(
    labels: pd.DataFrame,
    transactions: pd.DataFrame,
    accounts: pd.DataFrame,
    features: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    """Return one provenance-preserving alignment decision per source label."""
    gt = labels.copy()
    gt["pattern_start"] = pd.to_datetime(gt["pattern_start"], utc=True)
    gt["pattern_end"] = pd.to_datetime(gt["pattern_end"], utc=True)
    tx = transactions[["transaction_id", "timestamp", "sender_account_id", "receiver_account_id"]].copy()
    tx["timestamp"] = pd.to_datetime(tx["timestamp"], utc=True)
    owner = accounts.set_index("account_id")["owner_key"]

    evidence = gt[["ground_truth_id", "entity_key", "pattern_start", "pattern_end", "related_entity_ids"]].explode("related_entity_ids")
    evidence = evidence.rename(columns={"related_entity_ids": "transaction_id"})
    evidence = evidence.merge(tx, on="transaction_id", how="inner")
    evidence["affiliated"] = (
        evidence["entity_key"].eq("Account:" + evidence["sender_account_id"].astype(str))
        | evidence["entity_key"].eq("Account:" + evidence["receiver_account_id"].astype(str))
        | evidence["entity_key"].eq(evidence["sender_account_id"].map(owner))
        | evidence["entity_key"].eq(evidence["receiver_account_id"].map(owner))
    )
    evidence["before_cutoff"] = evidence["timestamp"] < evidence["pattern_start"]
    evidence["in_source_window"] = (
        evidence["timestamp"].ge(evidence["pattern_start"])
        & (evidence["pattern_end"].isna() | evidence["timestamp"].le(evidence["pattern_end"]))
    )
    evidence["after_source_window"] = evidence["pattern_end"].notna() & evidence["timestamp"].gt(evidence["pattern_end"])
    evidence["in_event_window"] = (
        evidence["affiliated"]
        & evidence["timestamp"].gt(evidence["pattern_start"])
        & evidence["pattern_end"].notna()
        & evidence["timestamp"].le(evidence["pattern_end"])
    )
    summary = evidence.groupby("ground_truth_id").agg(
        related_transaction_count=("transaction_id", "size"),
        affiliated_transaction_count=("affiliated", "sum"),
        related_before_cutoff_count=("before_cutoff", "sum"),
        related_in_source_window_count=("in_source_window", "sum"),
        related_after_source_window_count=("after_source_window", "sum"),
        aligned_future_event_count=("in_event_window", "sum"),
        first_related_transaction_at=("timestamp", "min"),
        last_related_transaction_at=("timestamp", "max"),
    )
    result = gt[[
        "ground_truth_id", "entity_key", "entity_type", "entity_id", "behavior_type",
        "risk_pattern", "is_anomalous", "pattern_start", "pattern_end",
    ]].merge(summary, left_on="ground_truth_id", right_index=True, how="left")
    count_columns = ["related_transaction_count", "affiliated_transaction_count", "related_before_cutoff_count", "related_in_source_window_count", "related_after_source_window_count", "aligned_future_event_count"]
    result[count_columns] = result[count_columns].fillna(0).astype("int64")
    history = features[["ground_truth_id", "history_tx_count"]].drop_duplicates("ground_truth_id")
    result = result.merge(history, on="ground_truth_id", how="left", validate="one_to_one")
    minimum = int(config["minimum_history_transactions"])
    result["history_status"] = np.where(
        result["history_tx_count"].fillna(0).eq(0), "cold_start_no_history",
        np.where(result["history_tx_count"].fillna(0).lt(minimum), "insufficient_history", "history_eligible"),
    )
    result["event_window_status"] = np.where(result["pattern_end"].isna(), "unbounded", "bounded")
    result["evidence_status"] = np.where(
        result["related_transaction_count"].eq(0), "no_transaction_evidence",
        np.where(result["affiliated_transaction_count"].eq(0), "unaffiliated_transaction_evidence",
                 np.where(result["aligned_future_event_count"].eq(0), "no_affiliated_future_event", "aligned_future_event")),
    )
    eligible = result["history_status"].eq("history_eligible")
    if config["require_bounded_event_window"]:
        eligible &= result["event_window_status"].eq("bounded")
    if config["require_affiliated_transaction_evidence"]:
        eligible &= result["affiliated_transaction_count"].gt(0)
    if config["require_event_after_cutoff"]:
        eligible &= result["aligned_future_event_count"].gt(0)
    result["predictive_eligible"] = eligible
    result["prediction_cutoff"] = result["pattern_start"]
    result["target_definition"] = "affiliated transaction event after cutoff within bounded source label window"
    result["source_label_unchanged"] = True
    return result


def _counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    return {str(key): int(value) for key, value in frame[column].value_counts(dropna=False).items()}


def run_alignment(project_dir: Path) -> dict[str, Any]:
    processed = project_dir / "data" / "processed"
    intelligence = project_dir / "data" / "intelligence"
    output = project_dir / "data" / "alignment"
    output.mkdir(parents=True, exist_ok=True)
    config = _json(project_dir / "config" / "intelligence.json")["label_alignment"]
    labels = pd.read_parquet(processed / "ground_truth_labels.parquet")
    transactions = pd.read_parquet(processed / "transaction_edges.parquet")
    accounts = pd.read_parquet(processed / "accounts.parquet")
    features = pd.read_parquet(intelligence / "label_feature_set.parquet")
    aligned = build_alignment_table(labels, transactions, accounts, features, config)
    aligned.to_parquet(output / "label_alignment.parquet", index=False)
    eligible_ids = set(aligned.loc[aligned["predictive_eligible"], "ground_truth_id"])
    population = features[features["ground_truth_id"].isin(eligible_ids)].copy()
    population.to_parquet(output / "predictive_population.parquet", index=False)

    related = aligned["related_transaction_count"].sum()
    affiliated = aligned["affiliated_transaction_count"].sum()
    offsets = (aligned["first_related_transaction_at"] - aligned["pattern_start"]).dt.total_seconds() / 86400
    ordered = aligned.sort_values(["entity_key", "pattern_start"])
    repeated = ordered[ordered.duplicated("entity_key", keep=False)]
    overlapping_rows = 0
    for _, group in repeated.groupby("entity_key"):
        prior_end = None
        for row in group.itertuples(index=False):
            if prior_end is not None and (pd.isna(prior_end) or row.pattern_start <= prior_end):
                overlapping_rows += 1
            if prior_end is None or pd.isna(prior_end) or (pd.notna(row.pattern_end) and row.pattern_end > prior_end):
                prior_end = row.pattern_end
    scenario_timing = {}
    for name, group in aligned.groupby("behavior_type"):
        scenario_timing[str(name)] = {
            "labels": int(len(group)), "positive_rate": float(group["is_anomalous"].mean()),
            "related_transactions": int(group["related_transaction_count"].sum()),
            "before_cutoff": int(group["related_before_cutoff_count"].sum()),
            "inside_source_window": int(group["related_in_source_window_count"].sum()),
            "after_source_window": int(group["related_after_source_window_count"].sum()),
            "history_eligible_rate": float(group["history_status"].eq("history_eligible").mean()),
        }
    before = _json(project_dir / "evaluation" / "evaluation.json")
    estimable = bool(len(population) and population["target"].nunique() == 2)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "prediction_unit": "typed entity + pattern_start cutoff + observable history + affiliated future transaction inside bounded pattern window",
        "source_rows": int(len(aligned)),
        "source_positive": int(aligned["is_anomalous"].sum()),
        "source_prevalence": float(aligned["is_anomalous"].mean()),
        "source_labels_modified": 0,
        "related_transaction_values": int(related),
        "affiliated_transaction_values": int(affiliated),
        "affiliation_rate": float(affiliated / related) if related else None,
        "related_transaction_timing": {
            "before_cutoff": int(aligned["related_before_cutoff_count"].sum()),
            "inside_source_window": int(aligned["related_in_source_window_count"].sum()),
            "after_source_window": int(aligned["related_after_source_window_count"].sum()),
            "median_first_related_offset_days": float(offsets.median()),
        },
        "scenario_timing": scenario_timing,
        "repeated_labels": {
            "rows": int(len(repeated)), "entities": int(repeated["entity_key"].nunique()),
            "entities_with_both_classes": int(aligned.groupby("entity_key")["is_anomalous"].nunique().gt(1).sum()),
            "overlapping_later_rows": int(overlapping_rows),
        },
        "history_status": _counts(aligned, "history_status"),
        "history_status_positive_rate": {
            str(name): float(group["is_anomalous"].mean())
            for name, group in aligned.groupby("history_status")
        },
        "event_window_status": _counts(aligned, "event_window_status"),
        "evidence_status": _counts(aligned, "evidence_status"),
        "predictive_eligible_rows": int(aligned["predictive_eligible"].sum()),
        "exclusion_reasons_are_nonexclusive": {
            "cold_or_insufficient_history": int(aligned["history_status"].ne("history_eligible").sum()),
            "unbounded_event_window": int(aligned["event_window_status"].eq("unbounded").sum()),
            "no_affiliated_transaction_evidence": int(aligned["affiliated_transaction_count"].eq(0).sum()),
            "no_aligned_future_event": int(aligned["aligned_future_event_count"].eq(0).sum()),
        },
        "before": {
            "evaluation_file": "evaluation/evaluation.json",
            "test_rows": before["supervised"]["test"]["rows"],
            "test_prevalence": before["supervised"]["test"]["prevalence"],
            "supervised_roc_auc": before["supervised"]["test"]["roc_auc"],
            "supervised_pr_auc": before["supervised"]["test"]["pr_auc"],
            "supervised_pr_auc_lift": before["supervised"]["test"]["pr_auc_lift_over_prevalence"],
            "anomaly_roc_auc": before["anomaly"]["test"]["roc_auc"],
            "rules_roc_auc": before["rules"]["test"]["roc_auc"],
            "feature_group_test": before["feature_group_test"],
            "scenario_test": before["scenario_test"],
        },
        "after": {
            "status": "eligible_for_evaluation" if estimable else "not_estimable",
            "reason": "Aligned predictive population contains both classes and may be evaluated with leakage-safe temporal/entity splits." if estimable else "Aligned predictive population is empty or does not contain both classes.",
            "rows": int(len(population)),
            "prevalence": float(population["target"].mean()) if len(population) else None,
            "supervised_roc_auc": None,
            "supervised_pr_auc": None,
            "supervised_pr_auc_lift": None,
            "anomaly_roc_auc": None,
            "rules_roc_auc": None,
            "scenario_test": {},
            "feature_group_test": {},
        },
        "decision": "Permit supervised evaluation only on predictive_population.parquet." if estimable else "Exclude labels from predictive evaluation until event provenance is repaired upstream.",
    }
    report_path = project_dir / "evaluation" / "alignment_evaluation.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
    validity = {
        "generated_at_utc": report["generated_at_utc"],
        "aligned_supervised_model": {"status": "eligible_not_yet_trained" if estimable else "not_trained", "reason": report["after"]["reason"]},
        "legacy_supervised_model": {"path": "artifacts/supervised_model.json", "status": "invalid_for_predictive_use", "allowed_use": "before-alignment diagnostic reproduction only"},
        "legacy_model_predictions": {"path": "signals/model_predictions.parquet", "status": "invalid_for_predictive_use"},
        "anomaly_and_rule_signals": {"status": "operational_patterns", "label_evaluation_status": "valid on aligned predictive population" if estimable else "invalid because source labels lack event provenance"},
        "required_gate": "Consumers must require data/alignment/label_alignment.parquet predictive_eligible=true before supervised training or label-based evaluation.",
    }
    artifacts = project_dir / "artifacts" / "VALIDITY.json"
    with artifacts.open("w", encoding="utf-8") as handle:
        json.dump(validity, handle, indent=2, sort_keys=True)
    signal_validity = aligned[["ground_truth_id", "history_status", "event_window_status", "evidence_status", "predictive_eligible"]].copy()
    signal_validity.to_parquet(project_dir / "signals" / "signal_validity.parquet", index=False)
    return report
