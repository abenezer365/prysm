"""End-to-end Phase 2 intelligence pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .evaluation import binary_metrics, scenario_metrics, temporal_entity_split
from .features import MODEL_FEATURES, AsOfFeatureBuilder, load_phase1, normalize_transactions
from .models import IsolationForestBaseline, LogisticBaseline, RobustPreprocessor
from .rules import RuleEngine


MONEY_FEATURES = {name for name in MODEL_FEATURES if "etb" in name}
FEATURE_GROUPS = {
    "transaction_behavior": ["history_tx_count", "history_median_amount_etb", "history_mean_amount_etb", "history_std_amount_etb", "invoice_link_rate_30d", "failed_rate_30d"],
    "velocity": [name for name in MODEL_FEATURES if name.startswith(("tx_count_", "inflow_etb_", "outflow_etb_")) or name in {"outflow_ratio_7d", "recent_amount_z", "recent_to_history_count_ratio"}],
    "foreign_currency": ["foreign_inflow_etb_30d", "foreign_inflow_count_30d", "currency_diversity_30d", "foreign_recent_to_history_ratio"],
    "relationships": ["counterparty_count_30d", "device_count_30d", "relationship_degree", "company_connection_count", "employer_relationship_count", "shared_device_relationship_count", "shared_address_relationship_count", "mean_relationship_confidence"],
}


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)


def _declared_split(features: pd.DataFrame, assignments_path: Path) -> dict[str, np.ndarray]:
    assignments = pd.read_parquet(assignments_path, columns=["ground_truth_id", "split"])
    if assignments["ground_truth_id"].duplicated().any():
        raise ValueError("Declared split contains duplicate ground_truth_id values")
    merged = features[["ground_truth_id", "entity_key", "as_of"]].merge(
        assignments, on="ground_truth_id", how="left", validate="one_to_one"
    )
    allowed = {"train", "validation", "test"}
    if merged["split"].isna().any() or not set(merged["split"]).issubset(allowed):
        raise ValueError("Declared split must assign every feature row to train, validation, or test")
    entity_splits = merged.groupby("entity_key")["split"].nunique()
    if entity_splits.gt(1).any():
        raise ValueError("Declared split leaks one entity across partitions")
    bounds = merged.groupby("split")["as_of"].agg(["min", "max"])
    if not (bounds.loc["train", "max"] < bounds.loc["validation", "min"] <= bounds.loc["validation", "max"] < bounds.loc["test", "min"]):
        raise ValueError("Declared split is not forward temporal")
    return {name: np.flatnonzero(merged["split"].eq(name).to_numpy()) for name in ("train", "validation", "test")}


def run_intelligence(
    project_dir: Path,
    reuse_features: bool = False,
    split_assignments_path: Path | None = None,
    population_path: Path | None = None,
    evaluation_validity: str | None = None,
) -> dict:
    processed = project_dir / "data" / "processed"
    output = project_dir / "data" / "intelligence"
    artifacts = project_dir / "artifacts"
    evaluations = project_dir / "evaluation"
    signals = project_dir / "signals"
    for directory in (output, artifacts, evaluations, signals):
        directory.mkdir(parents=True, exist_ok=True)
    with (project_dir / "config" / "intelligence.json").open(encoding="utf-8") as handle:
        config = json.load(handle)

    accounts, transactions, invoices, relationships = load_phase1(processed)
    labels = pd.read_parquet(processed / "ground_truth_labels.parquet")
    labels["pattern_start"] = pd.to_datetime(labels["pattern_start"], utc=True)
    feature_path = output / "label_feature_set.parquet"
    if reuse_features and feature_path.is_file() and (output / "normalized_transactions.parquet").is_file():
        features = pd.read_parquet(feature_path).drop(columns=["split"], errors="ignore")
    else:
        normalized = normalize_transactions(transactions, accounts, invoices)
        normalized.to_parquet(output / "normalized_transactions.parquet", index=False)
        features = AsOfFeatureBuilder(normalized, accounts, relationships, set(labels["entity_key"])).build_labels(labels)
    if population_path is not None:
        population_ids = set(pd.read_parquet(population_path, columns=["ground_truth_id"])["ground_truth_id"])
        features = features[features["ground_truth_id"].isin(population_ids)].reset_index(drop=True)
        if not len(features):
            raise ValueError("Aligned predictive population is empty")
    split = _declared_split(features, split_assignments_path) if split_assignments_path else temporal_entity_split(features)
    split_names = np.full(len(features), "", dtype=object)
    for name, indices in split.items():
        split_names[indices] = name
    features.assign(split=split_names).to_parquet(output / "label_feature_set.parquet", index=False)

    x = features[MODEL_FEATURES].to_numpy(float)
    y = features["target"].to_numpy(bool)
    log_columns = tuple(i for i, name in enumerate(MODEL_FEATURES) if name in MONEY_FEATURES)
    preprocessor = RobustPreprocessor(log_columns).fit(x[split["train"]])
    transformed = preprocessor.transform(x)

    supervised_config = config["supervised"]
    classifier = LogisticBaseline(supervised_config["learning_rate"], supervised_config["iterations"], supervised_config["l2"])
    classifier.fit(transformed[split["train"]], y[split["train"]])
    probabilities = classifier.predict_proba(transformed)
    predicted = probabilities >= supervised_config["threshold"]
    model_predictions = features[["ground_truth_id", "entity_key", "as_of"]].copy()
    model_predictions["probability"] = probabilities
    model_predictions["predicted_label"] = predicted
    model_predictions["model_version"] = "numpy-logistic-v1"
    model_predictions.to_parquet(signals / "model_predictions.parquet", index=False)

    anomaly_config = config["anomaly"]
    forest = IsolationForestBaseline(anomaly_config["trees"], anomaly_config["sample_size"], anomaly_config["contamination"], config["random_seed"])
    forest.fit(transformed[split["train"]])
    anomaly_scores, anomalies = forest.predict(transformed)
    anomaly_predictions = features[["ground_truth_id", "entity_key", "as_of"]].copy()
    anomaly_predictions["anomaly_score"] = anomaly_scores
    anomaly_predictions["is_anomaly"] = anomalies
    anomaly_predictions["model_version"] = "numpy-isolation-forest-v1"
    anomaly_predictions.to_parquet(signals / "anomaly_predictions.parquet", index=False)

    rule_engine = RuleEngine(config["rules"])
    findings, rule_positive = [], np.zeros(len(features), dtype=bool)
    for index, row in features.iterrows():
        row_findings = rule_engine.evaluate(row.to_dict())
        rule_positive[index] = bool(row_findings)
        for finding in row_findings:
            findings.append({"ground_truth_id": row["ground_truth_id"], "as_of": row["as_of"].isoformat(), **finding.to_dict()})
    with (signals / "rule_findings.jsonl").open("w", encoding="utf-8") as handle:
        for finding in findings:
            handle.write(json.dumps(finding, sort_keys=True) + "\n")

    results = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluation_validity": evaluation_validity or "legacy_unaligned_diagnostic_only; use evaluation/alignment_evaluation.json for the predictive eligibility decision",
        "split_method": "declared_forward_entity_disjoint" if split_assignments_path else "derived_forward_entity_purged_60_20_20",
        "split": {name: {"rows": int(len(indices)), "positive": int(y[indices].sum()), "min_as_of": features.iloc[indices]["as_of"].min().isoformat() if len(indices) else None, "max_as_of": features.iloc[indices]["as_of"].max().isoformat() if len(indices) else None} for name, indices in split.items()},
        "entity_overlap": {"train_validation": 0, "train_test": 0, "validation_test": 0},
        "purged_repeated_entity_rows": int(len(features) - sum(len(indices) for indices in split.values())),
        "supervised": {}, "anomaly": {}, "rules": {},
        "feature_count": len(MODEL_FEATURES), "feature_names": MODEL_FEATURES,
        "leakage_exclusions": ["ground_truth_id", "entity_key", "target", "scenario", "as_of", "behavior_type", "risk_pattern", "severity", "related_entity_ids"],
    }
    for name, indices in split.items():
        results["supervised"][name] = binary_metrics(y[indices], probabilities[indices], supervised_config["threshold"])
        results["anomaly"][name] = binary_metrics(y[indices], anomaly_scores[indices], forest.threshold_)
        results["rules"][name] = binary_metrics(y[indices], rule_positive[indices].astype(float), 0.5)
    test = split["test"]
    results["scenario_test"] = {
        "supervised": scenario_metrics(features.iloc[test]["scenario"], y[test], predicted[test]),
        "anomaly": scenario_metrics(features.iloc[test]["scenario"], y[test], anomalies[test]),
        "rules": scenario_metrics(features.iloc[test]["scenario"], y[test], rule_positive[test]),
    }
    results["supervised"]["coefficients"] = dict(sorted(zip(MODEL_FEATURES, classifier.coef_.tolist()), key=lambda item: abs(item[1]), reverse=True))
    results["feature_group_test"] = {}
    for group_name, group_features in FEATURE_GROUPS.items():
        columns = [MODEL_FEATURES.index(name) for name in group_features]
        group_log = tuple(i for i, name in enumerate(group_features) if name in MONEY_FEATURES)
        group_preprocessor = RobustPreprocessor(group_log).fit(x[split["train"]][:, columns])
        group_x = group_preprocessor.transform(x[:, columns])
        group_model = LogisticBaseline(supervised_config["learning_rate"], supervised_config["iterations"], supervised_config["l2"])
        group_model.fit(group_x[split["train"]], y[split["train"]])
        results["feature_group_test"][group_name] = binary_metrics(y[test], group_model.predict_proba(group_x[test]), supervised_config["threshold"])
    results["rules"]["finding_count"] = len(findings)

    _write_json(artifacts / "preprocessor.json", {"feature_names": MODEL_FEATURES, **preprocessor.to_dict()})
    _write_json(artifacts / "supervised_model.json", classifier.to_dict())
    _write_json(artifacts / "anomaly_model.json", forest.to_dict())
    _write_json(evaluations / "evaluation.json", results)
    _write_json(output / "FEATURESET.json", {"grain": "one typed entity at one ground-truth pattern_start cutoff", "rows": len(features), "features": MODEL_FEATURES, "metadata_columns": ["ground_truth_id", "entity_key", "as_of", "target", "scenario", "split", "transaction_ids_30d"], "as_of_inclusive": True})
    return results
