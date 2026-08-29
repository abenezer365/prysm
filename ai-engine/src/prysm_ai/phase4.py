"""Scenario-dataset integration, retraining, and scientific validation."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .data_readiness import FoundationBuilder
from .evaluation import binary_metrics
from .features import MODEL_FEATURES
from .investigation import InvestigationEngine
from .label_alignment import run_alignment
from .phase3_pipeline import run_phase3
from .pipeline import run_intelligence


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def verify_scenario_dataset(data_dir: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _json(manifest_path)
    errors = []
    for relative, details in manifest["files"].items():
        if not relative.startswith("data/"):
            continue
        path = data_dir / Path(relative).name
        if not path.is_file():
            errors.append(f"missing:{path.name}")
        elif _sha256(path) != details["sha256"]:
            errors.append(f"checksum:{path.name}")
    transactions = pd.read_parquet(data_dir / "transactions.parquet")
    labels = pd.read_parquet(data_dir / "ground_truth.parquet")
    accounts = pd.read_parquet(data_dir / "accounts.parquet")
    persons = set(pd.read_parquet(data_dir / "persons.parquet", columns=["person_id"])["person_id"].astype(str))
    companies = set(pd.read_parquet(data_dir / "companies.parquet", columns=["company_id"])["company_id"].astype(str))
    account_ids = set(accounts["account_id"].astype(str))
    tx_ids = set(transactions["transaction_id"].astype(str))
    original_source = data_dir.parents[2] / "synthetic-financial-generator" / "data" / "raw"
    schema_compatible = (
        pq.read_schema(data_dir / "transactions.parquet") == pq.read_schema(original_source / "transactions.parquet")
        and pq.read_schema(data_dir / "ground_truth.parquet") == pq.read_schema(original_source / "ground_truth.parquet")
    )
    evidence = labels[["ground_truth_id", "entity_type", "entity_id", "pattern_start", "pattern_end", "related_entity_ids"]].explode("related_entity_ids")
    evidence = evidence.merge(
        transactions[["transaction_id", "timestamp", "sender_account_id", "receiver_account_id"]],
        left_on="related_entity_ids", right_on="transaction_id", how="left",
    )
    owner = accounts.set_index("account_id").apply(lambda row: f"{row.owner_type}:{row.owner_id}", axis=1)
    entity_key = labels["entity_type"].astype(str) + ":" + labels["entity_id"].astype(str)
    evidence_key = evidence["entity_type"].astype(str) + ":" + evidence["entity_id"].astype(str)
    affiliated = (
        evidence_key.eq("Account:" + evidence["sender_account_id"].astype(str))
        | evidence_key.eq("Account:" + evidence["receiver_account_id"].astype(str))
        | evidence_key.eq(evidence["sender_account_id"].map(owner))
        | evidence_key.eq(evidence["receiver_account_id"].map(owner))
    )
    timestamp = pd.to_datetime(evidence["timestamp"], utc=True)
    cutoff = pd.to_datetime(evidence["pattern_start"], utc=True)
    end = pd.to_datetime(evidence["pattern_end"], utc=True) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    valid_entities = (
        labels["entity_type"].eq("Person") & labels["entity_id"].astype(str).isin(persons)
        | labels["entity_type"].eq("Company") & labels["entity_id"].astype(str).isin(companies)
        | labels["entity_type"].eq("Account") & labels["entity_id"].astype(str).isin(account_ids)
    )
    report = {
        "manifest_sha256": _sha256(manifest_path),
        "manifest_errors": errors,
        "transaction_rows": int(len(transactions)),
        "transaction_id_duplicates": int(transactions["transaction_id"].duplicated().sum()),
        "label_rows": int(len(labels)),
        "positive": int(labels["is_anomalous"].sum()),
        "negative": int((~labels["is_anomalous"]).sum()),
        "scenario_counts": {str(k): int(v) for k, v in labels["behavior_type"].value_counts().sort_index().items()},
        "invalid_labeled_entities": int((~valid_entities).sum()),
        "evidence_values": int(len(evidence)),
        "missing_evidence_transactions": int(evidence["transaction_id"].isna().sum()),
        "invalid_evidence_affiliations": int((~affiliated).sum()),
        "pre_or_at_cutoff_evidence": int((timestamp <= cutoff).sum()),
        "after_window_evidence": int((timestamp > end).sum()),
        "account_endpoint_errors": int((~transactions["sender_account_id"].isin(account_ids) | ~transactions["receiver_account_id"].isin(account_ids)).sum()),
        "schema_compatible": schema_compatible,
        "verified": not errors and transactions["transaction_id"].is_unique and valid_entities.all()
                    and evidence["transaction_id"].notna().all() and affiliated.all()
                    and (timestamp > cutoff).all() and (timestamp <= end).all() and schema_compatible,
    }
    if not report["verified"]:
        raise ValueError(f"Scenario dataset verification failed: {report}")
    return report


def _old_metrics(original_project: Path) -> dict[str, Any]:
    old = _json(original_project / "evaluation" / "evaluation.json")
    test = old["supervised"]["test"]
    return {
        "validity": "invalid_unaligned_diagnostic_only",
        "label_prevalence": test["prevalence"],
        "valid_predictive_rows": 0,
        "supervised_roc_auc": test["roc_auc"],
        "supervised_pr_auc": test["pr_auc"],
        "supervised_pr_auc_lift": test["pr_auc_lift_over_prevalence"],
        "anomaly_roc_auc": old["anomaly"]["test"]["roc_auc"],
        "rules_roc_auc": old["rules"]["test"]["roc_auc"],
    }


def _scenario_performance(run_dir: Path) -> dict[str, Any]:
    features = pd.read_parquet(run_dir / "data" / "intelligence" / "label_feature_set.parquet").reset_index(drop=True)
    model = pd.read_parquet(run_dir / "signals" / "model_predictions.parquet").set_index("ground_truth_id")
    anomaly = pd.read_parquet(run_dir / "signals" / "anomaly_predictions.parquet").set_index("ground_truth_id")
    findings = [json.loads(line) for line in (run_dir / "signals" / "rule_findings.jsonl").read_text(encoding="utf-8").splitlines() if line]
    rule_ids = {item["ground_truth_id"] for item in findings}
    test = features[features["split"].eq("test")].copy()
    test["supervised_score"] = test["ground_truth_id"].map(model["probability"])
    test["anomaly_score"] = test["ground_truth_id"].map(anomaly["anomaly_score"])
    test["rule_score"] = test["ground_truth_id"].isin(rule_ids).astype(float)
    normal = test[~test["target"]]
    result = {}
    for scenario, positives in test[test["target"]].groupby("scenario"):
        subset = pd.concat([normal, positives], ignore_index=True)
        y = subset["target"].to_numpy(bool)
        result[str(scenario)] = {
            "rows": int(len(subset)),
            "positive_rows": int(y.sum()),
            "supervised": binary_metrics(y, subset["supervised_score"].to_numpy(float), 0.5),
            "anomaly": binary_metrics(y, subset["anomaly_score"].to_numpy(float), float(_json(run_dir / "artifacts" / "anomaly_model.json")["threshold"])),
            "rules": binary_metrics(y, subset["rule_score"].to_numpy(float), 0.5),
        }
    return result


def _leakage_audit(run_dir: Path) -> dict[str, Any]:
    features = pd.read_parquet(run_dir / "data" / "intelligence" / "label_feature_set.parquet").reset_index(drop=True)
    labels = pd.read_parquet(run_dir / "data" / "processed" / "ground_truth_labels.parquet")
    evidence_ids = {
        str(value) for values in labels["related_entity_ids"] for value in (values if isinstance(values, (list, np.ndarray)) else [])
    }
    feature_tx_ids = {
        str(value) for values in features["transaction_ids_30d"] for value in (values if isinstance(values, (list, np.ndarray)) else [])
    }
    forbidden = {"ground_truth_id", "entity_key", "target", "scenario", "as_of", "behavior_type", "risk_pattern", "severity", "related_entity_ids"}
    test = features[features["split"].eq("test")]
    y = test["target"].to_numpy(bool)
    univariate = {}
    for feature in MODEL_FEATURES:
        metric = binary_metrics(y, test[feature].fillna(0).to_numpy(float), 0.5)
        auc = metric["roc_auc"]
        univariate[feature] = max(auc, 1.0 - auc) if auc is not None else None
    strongest = sorted(univariate.items(), key=lambda item: item[1] or 0.0, reverse=True)[:10]
    cutoff_score = pd.to_datetime(test["as_of"], utc=True).astype("int64").to_numpy(float)
    cutoff_auc = binary_metrics(y, cutoff_score, float(np.median(cutoff_score)))["roc_auc"]
    hard_failures = {
        "forbidden_model_columns": sorted(forbidden & set(MODEL_FEATURES)),
        "future_evidence_ids_in_pre_cutoff_features": len(evidence_ids & feature_tx_ids),
        "generated_scenario_transactions_in_pre_cutoff_features": sum(
            value.startswith("TX") and value[2:].isdigit() and int(value[2:]) > 700000 for value in feature_tx_ids
        ),
        "entity_split_overlap": int(features.groupby("entity_key")["split"].nunique().gt(1).sum()),
    }
    return {
        "status": "PASS" if not any([hard_failures["forbidden_model_columns"], hard_failures["future_evidence_ids_in_pre_cutoff_features"], hard_failures["generated_scenario_transactions_in_pre_cutoff_features"], hard_failures["entity_split_overlap"]]) else "FAIL",
        "hard_failures": hard_failures,
        "cutoff_only_roc_auc": cutoff_auc,
        "strongest_single_feature_absolute_roc_auc": dict(strongest),
        "interpretation": "High univariate ranking is reviewed as possible generator structure; only forbidden/future information constitutes a contract failure.",
    }


def _update_alignment_and_validity(run_dir: Path, original_project: Path, evaluation: dict[str, Any]) -> dict[str, Any]:
    alignment_path = run_dir / "evaluation" / "alignment_evaluation.json"
    alignment = _json(alignment_path)
    old = _old_metrics(original_project)
    new_test = evaluation["supervised"]["test"]
    alignment["before"] = old
    alignment["after"].update({
        "status": "valid_synthetic_scenario_evaluation",
        "rows": int(sum(item["rows"] for item in [evaluation["supervised"][name] for name in ("train", "validation", "test")])),
        "prevalence": new_test["prevalence"],
        "supervised_roc_auc": new_test["roc_auc"],
        "supervised_pr_auc": new_test["pr_auc"],
        "supervised_pr_auc_lift": new_test["pr_auc_lift_over_prevalence"],
        "anomaly_roc_auc": evaluation["anomaly"]["test"]["roc_auc"],
        "rules_roc_auc": evaluation["rules"]["test"]["roc_auc"],
        "scenario_test": evaluation["scenario_test"],
        "feature_group_test": evaluation["feature_group_test"],
        "scope": "synthetic scenario benchmark only",
    })
    _write_json(alignment_path, alignment)
    validity_path = run_dir / "artifacts" / "VALIDITY.json"
    validity = _json(validity_path)
    validity.update({
        "aligned_supervised_model": {
            "status": "valid_synthetic_scenario_evaluation",
            "artifact": "artifacts/supervised_model.json",
            "population": "data/alignment/predictive_population.parquet",
            "allowed_use": "synthetic future-scenario benchmark only",
            "is_real_world_fraud_probability": False,
        },
        "legacy_supervised_model": {
            "status": "superseded_for_scenario_benchmark",
            "allowed_use": "historical invalid baseline comparison only",
        },
        "model_predictions": {
            "status": "valid_synthetic_scenario_evaluation",
            "path": "signals/model_predictions.parquet",
            "is_real_world_fraud_probability": False,
        },
        "anomaly_and_rule_signals": {
            "status": "operational_patterns",
            "label_evaluation_status": "valid on aligned synthetic scenario benchmark",
        },
    })
    _write_json(validity_path, validity)
    return alignment


def _representative_investigations(run_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    features = pd.read_parquet(run_dir / "data" / "intelligence" / "label_feature_set.parquet")
    predictions = pd.read_parquet(run_dir / "signals" / "model_predictions.parquet")
    candidates = features[features["split"].eq("test") & features["target"]].merge(
        predictions[["ground_truth_id", "probability"]], on="ground_truth_id", how="inner"
    )
    engine = InvestigationEngine(run_dir, config)
    output_dir = run_dir / "investigations" / "scenarios"
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for scenario, group in candidates.groupby("scenario"):
        chosen = group.sort_values(["probability", "ground_truth_id"], ascending=[False, True]).iloc[0]
        investigation = engine.investigate(str(chosen.entity_key), pd.Timestamp(chosen.as_of), "predictive")
        path = output_dir / f"{scenario}.json"
        engine.write(investigation, path)
        results.append({
            "scenario": str(scenario), "ground_truth_id": str(chosen.ground_truth_id),
            "subject": str(chosen.entity_key), "cutoff": pd.Timestamp(chosen.as_of).isoformat(),
            "model_probability": float(chosen.probability), "investigation_id": investigation.investigation_id,
            "evidence_items": len(investigation.evidence), "assessment": investigation.assessment,
            "path": str(path.relative_to(run_dir)).replace("\\", "/"),
        })

    tx_ids = set(pd.read_parquet(run_dir / "data" / "processed" / "transaction_edges.parquet", columns=["transaction_id"])["transaction_id"].astype(str))
    rel_ids = set(pd.read_parquet(run_dir / "data" / "processed" / "relationship_edges.parquet", columns=["relationship_id"])["relationship_id"].astype(str))
    node_ids = set(pd.read_parquet(run_dir / "graph" / "nodes.parquet", columns=["node_key"])["node_key"].astype(str))
    requested_edges: set[str] = set()
    invalid_tx = invalid_rel = invalid_entities = duplicate_evidence = 0
    for item in results:
        payload = _json(run_dir / item["path"])
        evidence_ids = [evidence["evidence_id"] for evidence in payload["evidence"]]
        duplicate_evidence += len(evidence_ids) - len(set(evidence_ids))
        for evidence in payload["evidence"]:
            invalid_tx += sum(str(value) not in tx_ids for value in evidence["supporting_transaction_ids"])
            invalid_rel += sum(str(value) not in rel_ids for value in evidence["supporting_relationship_ids"])
            invalid_entities += sum(str(value) not in node_ids for value in evidence["supporting_entity_ids"])
            requested_edges.update(str(value) for value in evidence["supporting_edge_ids"])
    found_edges: set[str] = set()
    for path in (run_dir / "graph" / "edges").glob("*.parquet"):
        frame = pd.read_parquet(path, columns=["edge_id"])
        found_edges.update(frame.loc[frame["edge_id"].isin(requested_edges), "edge_id"].astype(str))
    validation = {
        "representative_investigations": len(results),
        "scenario_count": len({item["scenario"] for item in results}),
        "invalid_transaction_references": invalid_tx,
        "invalid_relationship_references": invalid_rel,
        "invalid_entity_references": invalid_entities,
        "invalid_edge_references": len(requested_edges - found_edges),
        "duplicate_evidence_ids": duplicate_evidence,
    }
    validation["status"] = "PASS" if all(value == 0 for key, value in validation.items() if key.startswith("invalid_") or key == "duplicate_evidence_ids") else "FAIL"
    return {"cases": results, "validation": validation}


def _report_markdown(report: dict[str, Any]) -> str:
    old, new = report["comparison"]["original"], report["comparison"]["scenario"]
    test = report["phase2"]["supervised"]["test"]
    scenarios = report["scenario_performance"]
    lines = [
        "# Phase 4 Scenario Integration, Retraining, and Validation", "",
        "## Scientific status", "",
        f"Dataset integration: **{report['dataset_integration']['status']}**  ",
        f"Alignment: **{report['alignment']['after']['status']}** ({report['alignment']['predictive_eligible_rows']:,} eligible rows)  ",
        f"Leakage audit: **{report['leakage_audit']['status']}**  ",
        f"Graph validation: **{report['graph']['status']}**  ",
        f"Evidence validation: **{report['evidence']['validation']['status']}**", "",
        "The supervised result is valid only for this controlled synthetic future-scenario benchmark. It is not a calibrated fraud probability and does not establish real-world performance.", "",
        "## Old versus new", "",
        "| Metric | Original | Scenario dataset |", "|---|---:|---:|",
        f"| Evaluation validity | {old['validity']} | {new['validity']} |",
        f"| Valid predictive rows | {old['valid_predictive_rows']:,} | {new['valid_predictive_rows']:,} |",
        f"| Test prevalence | {old['label_prevalence']:.3f} | {new['label_prevalence']:.3f} |",
        f"| Supervised ROC-AUC | {old['supervised_roc_auc']:.3f} | {new['supervised_roc_auc']:.3f} |",
        f"| Supervised PR-AUC | {old['supervised_pr_auc']:.3f} | {new['supervised_pr_auc']:.3f} |",
        f"| PR-AUC lift | {old['supervised_pr_auc_lift']:.3f} | {new['supervised_pr_auc_lift']:.3f} |",
        f"| Anomaly ROC-AUC | {old['anomaly_roc_auc']:.3f} | {new['anomaly_roc_auc']:.3f} |",
        f"| Rule ROC-AUC | {old['rules_roc_auc']:.3f} | {new['rules_roc_auc']:.3f} |", "",
        "## Valid supervised test metrics", "",
        f"ROC-AUC {test['roc_auc']:.6f}; PR-AUC {test['pr_auc']:.6f}; precision {test['precision']:.6f}; recall {test['recall']:.6f}; F1 {test['f1']:.6f}. Confusion matrix: `{test['confusion_matrix']}`.", "",
        "## Scenario-level test results", "",
        "| Scenario | Supervised ROC-AUC | PR-AUC | Recall | Rule recall | Anomaly ROC-AUC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in sorted(scenarios.items()):
        lines.append(f"| {name} | {metrics['supervised']['roc_auc']:.3f} | {metrics['supervised']['pr_auc']:.3f} | {metrics['supervised']['recall']:.3f} | {metrics['rules']['recall']:.3f} | {metrics['anomaly']['roc_auc']:.3f} |")
    lines += [
        "", "## GNN", "",
        f"Self-supervised structural link-reconstruction ROC-AUC: {report['gnn']['link_reconstruction_roc_auc']:.6f}. Supervised GNN status: `{report['gnn']['supervised_status']}`. The retrospective full-graph embedding was not used for predictive label evaluation because it contains post-cutoff edges.", "",
        "## Recommendation", "",
        report["recommendation"], "",
    ]
    return "\n".join(lines)


def run_phase4(original_project: Path, scenario_root: Path, run_dir: Path, verify_retraining: bool = True) -> dict[str, Any]:
    data_dir = scenario_root / "output" / "data"
    scenario_manifest = scenario_root / "output" / "MANIFEST.json"
    dataset_verification = verify_scenario_dataset(data_dir, scenario_manifest)
    config_dir = run_dir / "config"
    source_dir = run_dir / "data" / "source"
    config_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original_project / "config" / "intelligence.json", config_dir / "intelligence.json")
    shutil.copy2(scenario_root / "output" / "scenario_metadata.parquet", source_dir / "scenario_metadata.parquet")
    boundary = {
        "version": "prysm-scenario-integration-v1",
        "original_raw": "data/raw",
        "scenario_raw": "generator/ground-truth-scenario-generation/output/data",
        "scenario_manifest": "generator/ground-truth-scenario-generation/output/MANIFEST.json",
        "scenario_manifest_sha256": _sha256(scenario_manifest),
        "original_data_overwritten": False,
        "run_root": "ai-engine/runs/scenario-v1",
    }
    _write_json(run_dir / "DATA_BOUNDARY.json", boundary)

    foundation = FoundationBuilder(data_dir, run_dir / "data" / "processed", run_dir / "reports").run()
    split_path = source_dir / "scenario_metadata.parquet"
    run_intelligence(run_dir, split_assignments_path=split_path, evaluation_validity="pending_phase2_5_alignment")
    alignment = run_alignment(run_dir)
    if alignment["predictive_eligible_rows"] != dataset_verification["label_rows"]:
        raise RuntimeError(f"Alignment accepted {alignment['predictive_eligible_rows']} of {dataset_verification['label_rows']} rows")
    final_evaluation = run_intelligence(
        run_dir, reuse_features=True, split_assignments_path=split_path,
        population_path=run_dir / "data" / "alignment" / "predictive_population.parquet",
        evaluation_validity="valid_aligned_synthetic_scenario_evaluation",
    )
    deterministic_phase2 = True
    if verify_retraining:
        stable_first = json.loads(json.dumps(final_evaluation)); stable_first.pop("generated_at_utc", None)
        repeated = run_intelligence(
            run_dir, reuse_features=True, split_assignments_path=split_path,
            population_path=run_dir / "data" / "alignment" / "predictive_population.parquet",
            evaluation_validity="valid_aligned_synthetic_scenario_evaluation",
        )
        stable_second = json.loads(json.dumps(repeated)); stable_second.pop("generated_at_utc", None)
        deterministic_phase2 = stable_first == stable_second
        if not deterministic_phase2:
            raise AssertionError("Phase 2 retraining metrics changed on deterministic rerun")
        final_evaluation = repeated
    alignment = _update_alignment_and_validity(run_dir, original_project, final_evaluation)

    phase3 = run_phase3(run_dir)
    config = _json(run_dir / "config" / "intelligence.json")
    evidence = _representative_investigations(run_dir, config)
    scenario_performance = _scenario_performance(run_dir)
    leakage = _leakage_audit(run_dir)
    old = _old_metrics(original_project)
    test = final_evaluation["supervised"]["test"]
    comparison_new = {
        "validity": "valid_aligned_synthetic_scenario_evaluation",
        "label_prevalence": test["prevalence"],
        "valid_predictive_rows": alignment["predictive_eligible_rows"],
        "supervised_roc_auc": test["roc_auc"],
        "supervised_pr_auc": test["pr_auc"],
        "supervised_pr_auc_lift": test["pr_auc_lift_over_prevalence"],
        "anomaly_roc_auc": final_evaluation["anomaly"]["test"]["roc_auc"],
        "rules_roc_auc": final_evaluation["rules"]["test"]["roc_auc"],
    }
    gnn = {
        "status": "self_supervised_structural_signal",
        "link_reconstruction_roc_auc": phase3["gnn"]["link_reconstruction_roc_auc"],
        "evaluation_validity": phase3["gnn"]["evaluation_status"],
        "supervised_status": phase3["supervised_gnn_evaluation"]["status"],
        "supervised_metrics": None,
        "reason": phase3["supervised_gnn_evaluation"]["reason"],
    }
    graph_validation = phase3["graph_validation"]
    graph_pass = all(graph_validation.get(name, 0) == 0 for name in ["invalid_endpoints", "duplicate_edge_id_rows", "duplicate_semantic_edge_rows", "self_loops", "temporal_end_before_start"])
    report = {
        "version": "prysm-phase4-retrain-validation-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_integration": {"status": "READY", "boundary": boundary, "verification": dataset_verification},
        "foundation": {"source": foundation["source"], "processed_manifest": "data/processed/MANIFEST.json"},
        "alignment": alignment,
        "phase2": final_evaluation,
        "scenario_performance": scenario_performance,
        "leakage_audit": leakage,
        "comparison": {"original": old, "scenario": comparison_new},
        "graph": {"status": "PASS" if graph_pass else "FAIL", "validation": graph_validation, "manifest": phase3["graph_manifest"]},
        "gnn": gnn,
        "fusion": {
            "status": "PASS" if evidence["validation"]["status"] == "PASS" else "FAIL",
            "assessment_type": "uncalibrated_attention_assessment",
            "representative_cases": len(evidence["cases"]),
            "calibrated": False,
        },
        "evidence": evidence,
        "reproducibility": {
            "phase2_retraining_metrics_identical": deterministic_phase2,
            "scenario_manifest_sha256": _sha256(scenario_manifest),
            "intelligence_config_sha256": _sha256(run_dir / "config" / "intelligence.json"),
            "feature_set_sha256": _sha256(run_dir / "data" / "intelligence" / "label_feature_set.parquet"),
            "supervised_model_sha256": _sha256(run_dir / "artifacts" / "supervised_model.json"),
            "graph_manifest_sha256": _sha256(run_dir / "graph" / "MANIFEST.json"),
            "gnn_artifact_sha256": _sha256(run_dir / "artifacts" / "gnn_encoder.json"),
        },
        "limitations": [
            "The target is controlled synthetic future-scenario occurrence, not observed real-world fraud or AML outcome.",
            "Scenario assignment may not be predictable from pre-cutoff behavior; near-random predictive performance is a valid result.",
            "The final fusion remains uncalibrated and is not a fraud probability.",
            "Supervised GNN evaluation is withheld until a batched cutoff-safe training path exists; retrospective embeddings contain future edges.",
            "GraphStore remains disk-scan based and is not optimized for interactive latency.",
        ],
        "recommendation": "Use these results as the valid synthetic benchmark baseline. Improve scenario causal precursors and add a batched cutoff-safe GNN training/evaluation path before claiming predictive graph performance; do not tune thresholds or models solely to inflate scores.",
    }
    evaluation_dir = run_dir / "evaluation"
    _write_json(evaluation_dir / "phase4_retrain_validation.json", report)
    (run_dir / "PHASE_4_RETRAIN_VALIDATION_REPORT.md").write_text(_report_markdown(report), encoding="utf-8")
    manifest_files = [
        run_dir / "DATA_BOUNDARY.json", run_dir / "data" / "processed" / "MANIFEST.json",
        run_dir / "data" / "intelligence" / "FEATURESET.json", run_dir / "data" / "alignment" / "predictive_population.parquet",
        run_dir / "artifacts" / "supervised_model.json", run_dir / "artifacts" / "anomaly_model.json",
        run_dir / "artifacts" / "gnn_encoder.json", run_dir / "evaluation" / "evaluation.json",
        run_dir / "evaluation" / "alignment_evaluation.json", run_dir / "evaluation" / "phase3_evaluation.json",
        run_dir / "evaluation" / "phase4_retrain_validation.json", run_dir / "PHASE_4_RETRAIN_VALIDATION_REPORT.md",
    ]
    run_manifest = {
        "version": report["version"], "dataset_manifest_sha256": _sha256(scenario_manifest),
        "files": {str(path.relative_to(run_dir)).replace("\\", "/"): _sha256(path) for path in manifest_files},
    }
    _write_json(run_dir / "RUN_MANIFEST.json", run_manifest)
    return report
