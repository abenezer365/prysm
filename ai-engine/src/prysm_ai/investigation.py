"""Investigator-facing graph, fusion, confidence, and evidence orchestration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .contracts import InvestigationResult, SignalComponent
from .evidence import EvidenceEngine
from .fusion import SignalFusion
from .features import MODEL_FEATURES, AsOfFeatureBuilder, load_phase1, normalize_transactions
from .graph import GraphStore
from .gnn import encode_temporal_subgraph
from .models import IsolationForestBaseline, LogisticBaseline, RobustPreprocessor
from .rules import RuleEngine


def _bounded(value: float) -> float:
    return float(min(max(value, 0.0), 1.0))


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict): return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)): return [_jsonable(v) for v in value]
    if isinstance(value, (pd.Timestamp,)): return value.isoformat()
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,)): return float(value)
    if pd.isna(value): return None
    return value


class InvestigationEngine:
    def __init__(self, project_dir: Path, config: dict[str, Any]):
        self.project_dir, self.config = project_dir, config
        self.graph_store = GraphStore(project_dir / "graph")
        self.gnn_artifact = json.loads((project_dir / "artifacts" / "gnn_encoder.json").read_text(encoding="utf-8"))
        self.features = pd.read_parquet(project_dir / "data" / "intelligence" / "label_feature_set.parquet")
        self.anomalies = pd.read_parquet(project_dir / "signals" / "anomaly_predictions.parquet").set_index("ground_truth_id")
        self.model_predictions = pd.read_parquet(project_dir / "signals" / "model_predictions.parquet").set_index("ground_truth_id")
        validity_path = project_dir / "artifacts" / "VALIDITY.json"
        self.validity = json.loads(validity_path.read_text(encoding="utf-8")) if validity_path.is_file() else {}
        self.rules = [json.loads(line) for line in (project_dir / "signals" / "rule_findings.jsonl").read_text(encoding="utf-8").splitlines() if line]
        accounts, transactions, invoices, relationships = load_phase1(project_dir / "data" / "processed")
        normalized_path = project_dir / "data" / "intelligence" / "normalized_transactions.parquet"
        normalized = pd.read_parquet(normalized_path) if normalized_path.is_file() else normalize_transactions(transactions, accounts, invoices)
        self.normalized_transactions, self.accounts, self.relationships = normalized, accounts, relationships
        self.preprocessor = RobustPreprocessor.from_dict(json.loads((project_dir / "artifacts" / "preprocessor.json").read_text(encoding="utf-8")))
        self.supervised_model = LogisticBaseline.from_dict(json.loads((project_dir / "artifacts" / "supervised_model.json").read_text(encoding="utf-8")))
        self.anomaly_model = IsolationForestBaseline.from_dict(json.loads((project_dir / "artifacts" / "anomaly_model.json").read_text(encoding="utf-8")))
        self.rule_engine = RuleEngine(config["rules"])
        self.fusion = SignalFusion(config["fusion"])
        self.evidence_engine = EvidenceEngine(**config["evidence"])

    def _snapshot(self, subject: str, cutoff: pd.Timestamp) -> pd.Series | None:
        candidates = self.features[self.features.entity_key.eq(subject) & self.features.as_of.le(cutoff)]
        return candidates.sort_values(["as_of", "ground_truth_id"], kind="stable").iloc[-1] if len(candidates) else None

    def investigate(self, subject: str, cutoff: pd.Timestamp, mode: str = "predictive") -> InvestigationResult:
        cutoff = pd.Timestamp(cutoff)
        graph_cfg, scales = self.config["graph"], self.config["fusion"]["scales"]
        nodes, edges = self.graph_store.subgraph(subject, cutoff, graph_cfg["max_hops"], graph_cfg["max_nodes"],
                                                  graph_cfg["default_lookback_days"], mode,
                                                  set(graph_cfg["allowed_edge_types"]) or None, graph_cfg["minimum_confidence"])
        local_embeddings, local_features = encode_temporal_subgraph(nodes, edges, self.gnn_artifact)
        local_index = pd.Index(local_features.node_key.astype(str)); subject_position = int(local_index.get_loc(subject))
        neighbor_keys = set(edges.loc[edges.source_key.eq(subject), "target_key"]) | set(edges.loc[edges.target_key.eq(subject), "source_key"])
        neighbor_positions = local_index.get_indexer(sorted(neighbor_keys)); neighbor_positions = neighbor_positions[neighbor_positions >= 0]
        if len(neighbor_positions):
            cosine = float(local_embeddings[subject_position] @ local_embeddings[neighbor_positions].mean(axis=0))
            novelty = _bounded((1.0 - cosine) / 2.0)
        else:
            novelty = 0.0
        graph_row = local_features.iloc[subject_position].drop(labels=["node_key", "node_type"]).to_dict()
        graph_scales = graph_cfg["signal_scales"]
        graph_strength = np.mean([
            _bounded(float(graph_row["degree"]) / graph_scales["degree"]),
            _bounded(float(graph_row["edge_type_diversity"]) / graph_scales["edge_type_diversity"]),
            _bounded(float(len(nodes)) / graph_scales["neighborhood_nodes"]),
        ])
        graph_row["structural_anomaly_score"] = float(graph_strength)
        feature_builder = AsOfFeatureBuilder(self.normalized_transactions, self.accounts, self.relationships, {subject})
        snapshot = pd.Series({"ground_truth_id": f"runtime:{subject}:{cutoff.isoformat()}", "entity_key": subject, "as_of": cutoff, **feature_builder.build_one(subject, cutoff)})
        evidence = []
        graph_evidence = self.evidence_engine.graph_summary(subject, graph_row, nodes, edges, novelty); evidence.append(graph_evidence)
        graph_confidence = _bounded(float(graph_row["degree"]) / graph_scales["degree"])
        components: dict[str, SignalComponent] = {
            "graph": SignalComponent("graph", "available", graph_strength, graph_confidence, "Cutoff-valid bounded structural intensity; centrality alone is not risk.", [graph_evidence.evidence_id]),
            "gnn": SignalComponent("gnn", "available", novelty, 0.4 * graph_confidence, "Cutoff-valid unsupervised neighborhood contrast; no valid labels were used.", [graph_evidence.evidence_id]),
            "supervised_prediction": SignalComponent("supervised_prediction", "unavailable", None, 0.0, "No valid aligned model snapshot is available."),
        }
        snapshot_rules: list[dict[str, Any]] = []
        if snapshot is not None:
            history_confidence = _bounded(float(snapshot.history_tx_count) / scales["history_transactions"])
            transaction_volume = float(snapshot.inflow_etb_30d + snapshot.outflow_etb_30d)
            transaction_strength = 0.5 * _bounded(float(snapshot.tx_count_30d) / scales["transaction_count_30d"]) + 0.5 * _bounded(transaction_volume / scales["transaction_volume_etb_30d"])
            behavior_strength = _bounded(abs(float(snapshot.recent_amount_z)) / scales["behavior_z"])
            velocity_strength = max(_bounded(float(snapshot.recent_to_history_count_ratio) / scales["velocity_ratio"]), _bounded(float(snapshot.outflow_ratio_7d) / scales["velocity_ratio"]))
            transaction_ids = [str(v) for v in snapshot.transaction_ids_30d]
            phase_evidence = [
                self.evidence_engine.phase2_feature(subject, "transaction_activity", "Thirty-day transaction activity available at cutoff.", history_confidence, {"count_30d": snapshot.tx_count_30d, "volume_etb_30d": transaction_volume}, transaction_ids, snapshot.as_of.isoformat()),
                self.evidence_engine.phase2_feature(subject, "behavior_change", "Recent transaction amount deviation from entity history.", history_confidence, {"recent_amount_z": snapshot.recent_amount_z, "history_transactions": snapshot.history_tx_count}, transaction_ids, snapshot.as_of.isoformat()),
                self.evidence_engine.phase2_feature(subject, "velocity", "Recent frequency and outflow ratios relative to history.", history_confidence, {"activity_ratio": snapshot.recent_to_history_count_ratio, "outflow_ratio_7d": snapshot.outflow_ratio_7d}, transaction_ids, snapshot.as_of.isoformat()),
            ]
            evidence.extend(phase_evidence)
            components.update({
                "transaction": SignalComponent("transaction", "available", transaction_strength, history_confidence, "Observed 30-day count and ETB volume.", [phase_evidence[0].evidence_id]),
                "behavior": SignalComponent("behavior", "available", behavior_strength, history_confidence, "Deviation from the entity's observable history.", [phase_evidence[1].evidence_id]),
                "velocity": SignalComponent("velocity", "available", velocity_strength, history_confidence, "Recent rate and outflow measures.", [phase_evidence[2].evidence_id]),
            })
            snapshot_rules = [{"ground_truth_id": snapshot.ground_truth_id, "as_of": pd.Timestamp(snapshot.as_of).isoformat(), **item.to_dict()} for item in self.rule_engine.evaluate(snapshot.to_dict())]
            rule_evidence = [self.evidence_engine.from_rule(subject, item) for item in snapshot_rules]; evidence.extend(rule_evidence)
            components["rule"] = SignalComponent("rule", "available", max((float(item["score"]) for item in snapshot_rules), default=0.0), 1.0 if snapshot_rules else history_confidence, "Maximum configured rule strength at the selected snapshot.", [item.evidence_id for item in rule_evidence])
            model_input = self.preprocessor.transform(snapshot[MODEL_FEATURES].to_numpy(float).reshape(1, -1))
            anomaly_score, anomaly_flag = self.anomaly_model.predict(model_input)
            anomaly_confidence = 0.4 * history_confidence
            anomaly_evidence = self.evidence_engine.anomaly_signal(subject, float(anomaly_score[0]), "numpy-isolation-forest-v1", anomaly_confidence, transaction_ids, snapshot.as_of.isoformat())
            evidence.append(anomaly_evidence)
            components["anomaly"] = SignalComponent("anomaly", "available", _bounded(float(anomaly_score[0])), anomaly_confidence, f"Isolation Forest behavioral anomaly ({'threshold exceeded' if bool(anomaly_flag[0]) else 'within learned threshold'}); not a fraud probability.", [anomaly_evidence.evidence_id])
            probability = float(self.supervised_model.predict_proba(model_input)[0])
            supervised_evidence = self.evidence_engine.supervised_signal(subject, probability, "numpy-logistic-v1", transaction_ids, snapshot.as_of.isoformat())
            evidence.append(supervised_evidence)
            components["supervised_prediction"] = SignalComponent("supervised_prediction", "available", probability, history_confidence, "Model inference for the synthetic future-scenario target; not calibrated for real-world fraud.", [supervised_evidence.evidence_id])

        assessment = self.fusion.combine(components)
        selected = self.evidence_engine.limit(evidence)
        subject_node = self.graph_store.nodes.loc[subject]
        investigation_id = "INV:" + hashlib.sha256(f"{subject}|{cutoff.isoformat()}|{mode}".encode()).hexdigest()[:16]
        limitations = [
            "Supervised output is valid only for the aligned synthetic scenario benchmark and is not a real-world fraud probability.",
            "The GNN component is an unsupervised structural representation, not a fraud probability.",
            "High graph centrality or transaction volume is contextual intelligence, not an accusation.",
            "Account and invoice chronology contain known synthetic inconsistencies.",
        ]
        return InvestigationResult(
            investigation_id, {"entity_key": subject, "node_type": subject_node.node_type, "source_id": subject_node.source_id},
            {"mode": mode, "cutoff": cutoff.isoformat(), "lookback_days": graph_cfg["default_lookback_days"], "future_edges_included": mode == "retrospective"},
            {"nodes": len(nodes), "edges": len(edges), "node_types": nodes.node_type.value_counts().to_dict(), "edge_types": edges.edge_type.value_counts().to_dict() if len(edges) else {}, "subject_features": graph_row},
            {name: item.to_dict() for name, item in components.items()}, assessment, assessment["confidence"],
            {"rules": snapshot_rules, "supervised_model": {"status": components["supervised_prediction"].status, "reason": components["supervised_prediction"].reason}},
            [item.to_dict() for item in selected], limitations,
            {"graph_version": "prysm-financial-graph-v1", "gnn_version": "relational-graphsage-structural-v1", "configuration": "config/intelligence.json", "source_labels_used": components["supervised_prediction"].status == "available", "graph_and_gnn_view": "recomputed from cutoff-valid bounded subgraph"},
        )

    @staticmethod
    def write(result: InvestigationResult, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(_jsonable(result.to_dict()), handle, indent=2, sort_keys=True)
