"""Structured evidence derived only from source-backed graph/intelligence facts."""

from __future__ import annotations

import hashlib
from typing import Any

import pandas as pd

from .contracts import EvidenceItem


def _id(subject: str, source: str, kind: str) -> str:
    return "EVD:" + hashlib.sha256(f"{subject}|{source}|{kind}".encode()).hexdigest()[:16]


class EvidenceEngine:
    def __init__(self, maximum_items: int = 25, minimum_signal_strength: float = 0.25):
        self.maximum_items, self.minimum_signal_strength = maximum_items, minimum_signal_strength

    def from_rule(self, subject: str, finding: dict[str, Any]) -> EvidenceItem:
        return EvidenceItem(
            _id(subject, finding["rule_id"], finding.get("ground_truth_id", "")), subject, "rule_engine", finding["rule_id"],
            finding["explanation"], finding["severity"], float(finding["score"]),
            [str(v) for v in finding.get("entity_ids", []) if str(v) != subject],
            [str(v) for v in finding.get("transaction_ids", [])], [], [], finding.get("measurements", {}),
            [finding["as_of"]] if finding.get("as_of") else [],
            {"source": "signals/rule_findings.jsonl", "derivation": "configured rule over Phase 2 as-of features"},
        )

    def graph_summary(self, subject: str, node_features: dict[str, Any], nodes: pd.DataFrame, edges: pd.DataFrame,
                      novelty: float) -> EvidenceItem:
        transaction_ids = sorted(str(v) for v in edges.transaction_id.dropna().unique())[:100] if len(edges) else []
        relationship_ids = sorted(str(v) for v in edges.relationship_id.dropna().unique())[:100] if len(edges) else []
        edge_ids = sorted(str(v) for v in edges.edge_id.unique())[:100] if len(edges) else []
        timestamps = sorted(pd.to_datetime(edges.event_time.dropna(), utc=True).astype(str).unique())[-10:] if len(edges) else []
        measurements = {name: node_features.get(name) for name in ["degree", "edge_type_diversity", "network_transaction_count", "network_transaction_volume_etb", "network_unique_counterparties", "network_unique_sources", "network_unique_destinations", "network_outflow_ratio", "connected_account_count", "connected_company_count", "component_size", "structural_anomaly_score"]}
        measurements.update({"bounded_subgraph_nodes": len(nodes), "bounded_subgraph_edges": len(edges), "gnn_neighborhood_novelty": novelty})
        return EvidenceItem(
            _id(subject, "graph", "summary"), subject, "graph_intelligence", "network_structure",
            "Bounded temporal neighborhood and source-backed structural measurements.", "info",
            float(min(max(node_features.get("structural_anomaly_score", 0.0), 0), 1)),
            sorted(set(nodes.node_key.astype(str)) - {subject})[:100], transaction_ids, relationship_ids, edge_ids,
            measurements, [str(value) for value in timestamps],
            {"source": "graph node/edge artifacts", "derivation": "typed temporal degree, component, transaction, and neighborhood aggregation"},
        )

    def phase2_feature(self, subject: str, name: str, description: str, confidence: float,
                       measurements: dict[str, Any], transaction_ids: list[str], as_of: str) -> EvidenceItem:
        return EvidenceItem(
            _id(subject, "phase2", name), subject, "phase2_features", name, description, "info", confidence,
            [], [str(value) for value in transaction_ids], [], [], measurements, [as_of],
            {"source": "data/intelligence/label_feature_set.parquet", "derivation": "inclusive as-of temporal aggregation"},
        )

    def anomaly_signal(self, subject: str, score: float, model_version: str, confidence: float,
                       transaction_ids: list[str], as_of: str) -> EvidenceItem:
        return EvidenceItem(
            _id(subject, "anomaly", as_of), subject, "anomaly_model", "behavioral_anomaly",
            "Unsupervised Phase 2 behavioral isolation score at the selected snapshot.", "info", confidence,
            [], [str(value) for value in transaction_ids], [], [],
            {"anomaly_score": score, "model_version": model_version}, [as_of],
            {"source": "signals/anomaly_predictions.parquet", "model_artifact": "artifacts/anomaly_model.json",
             "derivation": "isolation forest over leakage-safe Phase 2 features; no label meaning"},
        )

    def supervised_signal(self, subject: str, probability: float, model_version: str,
                          transaction_ids: list[str], as_of: str) -> EvidenceItem:
        return EvidenceItem(
            _id(subject, "supervised", as_of), subject, "supervised_model", "future_scenario_prediction",
            "Leakage-safe baseline estimate for the synthetic future-scenario target; not a real-world fraud probability.",
            "info", float(min(max(probability, 0.0), 1.0)), [],
            [str(value) for value in transaction_ids], [], [],
            {"synthetic_scenario_probability": probability, "model_version": model_version}, [as_of],
            {"source": "signals/model_predictions.parquet", "model_artifact": "artifacts/supervised_model.json",
             "derivation": "regularized logistic regression over pre-cutoff Phase 2 features"},
        )

    def limit(self, items: list[EvidenceItem]) -> list[EvidenceItem]:
        return sorted(items, key=lambda item: (-item.confidence, item.evidence_id))[: self.maximum_items]
