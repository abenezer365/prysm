"""Build graph intelligence, structural GNN artifacts, and a demo investigation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .gnn import build_embeddings
from .graph import CanonicalGraphBuilder
from .graph_features import build_graph_features
from .investigation import InvestigationEngine


def run_phase3(project_dir: Path, reuse_graph: bool = False, reuse_derived: bool = False) -> dict[str, Any]:
    with (project_dir / "config" / "intelligence.json").open(encoding="utf-8") as handle:
        config = json.load(handle)
    graph_dir = project_dir / "graph"
    if reuse_graph and (graph_dir / "MANIFEST.json").is_file():
        manifest = json.loads((graph_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    else:
        manifest = CanonicalGraphBuilder(project_dir / "data" / "processed", graph_dir).build()
    if reuse_derived:
        validation = json.loads((project_dir / "evaluation" / "graph_validation.json").read_text(encoding="utf-8"))
        artifact = json.loads((project_dir / "artifacts" / "gnn_encoder.json").read_text(encoding="utf-8"))
        gnn = {"rows": validation["node_count"], "embedding_size": artifact["hidden_dim"], "model_version": artifact["model_version"],
               "labels_used": False, "link_reconstruction_roc_auc": artifact["evaluation"]["roc_auc"], "evaluation_status": artifact["evaluation_status"]}
    else:
        validation = build_graph_features(graph_dir, project_dir / "evaluation" / "graph_validation.json")
        gnn = build_embeddings(graph_dir, project_dir / "artifacts" / "gnn_encoder.json", config["gnn"])
    findings = [json.loads(line) for line in (project_dir / "signals" / "rule_findings.jsonl").read_text(encoding="utf-8").splitlines() if line]
    nodes = set(pd.read_parquet(graph_dir / "nodes.parquet", columns=["node_key"]).node_key)
    candidates = [item for item in findings if item["entity_ids"] and item["entity_ids"][0] in nodes]
    if candidates:
        chosen = sorted(candidates, key=lambda item: (-float(item["score"]), item["as_of"], item["entity_ids"][0]))[0]
        subject, cutoff = chosen["entity_ids"][0], pd.Timestamp(chosen["as_of"])
    else:
        top = pd.read_parquet(graph_dir / "node_features.parquet").sort_values(["structural_anomaly_score", "node_key"], ascending=[False, True]).iloc[0]
        subject, cutoff = top.node_key, pd.Timestamp(config["graph"]["default_cutoff"])
    engine = InvestigationEngine(project_dir, config)
    result = engine.investigate(subject, cutoff, "predictive")
    engine.write(result, project_dir / "investigations" / "demo_investigation.json")
    alignment_path = project_dir / "evaluation" / "alignment_evaluation.json"
    alignment = json.loads(alignment_path.read_text(encoding="utf-8")) if alignment_path.is_file() else {"after": {"status": "not_estimable"}}
    label_status = alignment["after"]["status"]
    label_estimable = label_status in {"eligible_for_evaluation", "valid_synthetic_scenario_evaluation"}
    evaluation = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(), "graph_manifest": manifest,
        "graph_validation": validation, "gnn": gnn,
        "demonstration": {"subject": subject, "cutoff": cutoff.isoformat(), "investigation_id": result.investigation_id,
                          "evidence_items": len(result.evidence), "bounded_nodes": result.graph_summary["nodes"], "bounded_edges": result.graph_summary["edges"]},
        "valid_evaluations": ["graph integrity", "typed endpoints", "temporal filtering", "bounded traversal", "deterministic GNN forward", "evidence provenance"],
        "supervised_gnn_evaluation": {
            "status": "NOT_RUN_CUTOFF_SAFE_HEAD_REQUIRED" if label_estimable else "NOT VALID FOR PREDICTIVE CLAIMS",
            "metrics": None,
            "reason": "Labels are valid, but the stored full-graph embeddings are retrospective and cannot train a predictive head without future-edge leakage; a batched cutoff-safe GNN training path is not implemented." if label_estimable else "Phase 2.5 aligned predictive population is empty.",
        },
    }
    with (project_dir / "evaluation" / "phase3_evaluation.json").open("w", encoding="utf-8") as handle:
        json.dump(evaluation, handle, indent=2, sort_keys=True)
    validity_path = project_dir / "artifacts" / "VALIDITY.json"
    validity = json.loads(validity_path.read_text(encoding="utf-8")); validity["graph_gnn"] = {
        "status": "self_supervised_structural_signal", "supervised_metrics": "not_run_cutoff_safe_head_required" if label_estimable else "not_estimable",
        "artifact": "artifacts/gnn_encoder.json", "labels_used": False,
    }
    validity_path.write_text(json.dumps(validity, indent=2, sort_keys=True), encoding="utf-8")
    return evaluation
