"""The public intelligence interface: facts + subject + cutoff -> evidence JSON."""
from dataclasses import asdict
import hashlib
import json

from . import VERSION
from .data import utc
from .evidence import Lead, annotate_graph, build_evidence
from .features import build_features
from .fusion import fuse
from .graph import NODE_FEATURES, graph_dto, graph_sample
from .network import network_leads
from .rules import rule_leads


class IntelligenceEngine:
    def __init__(self, dataset, config, anomaly=None, gnn=None, model_provenance=None):
        self.dataset, self.config, self.anomaly, self.gnn = dataset, config, anomaly, gnn
        self.model_provenance = model_provenance or {}
        identity = {"engine_version": VERSION, "dataset": dataset.checksum, "config": config,
                    "anomaly": anomaly.to_dict() if anomaly else None, "gnn": gnn.to_dict() if gnn else None,
                    "training": self.model_provenance}
        self.fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True, allow_nan=False).encode()).hexdigest()

    def investigate(self, subject, cutoff):
        s = self.dataset.snapshot(subject, cutoff, self.config)
        f = build_features(s)
        # Business-account activity belongs to the observed graph even when the
        # owner's personal account is quiet. Anomaly keeps its personal window.
        has_graph_activity = bool(s.transactions.timestamp.ge(s.window_start).any())
        rules, checks = rule_leads(s, f, self.config["rules"])
        network, network_summary = network_leads(s, f, self.config["rules"])
        graph = graph_dto(s)
        if s.truncated:
            rules, network = [], []
            checks = {key: "unavailable" for key in checks}
        if network_summary["search_truncated"]:
            network = []
        leads = [*rules, *network]
        trained_until = self.model_provenance.get("training_cutoff")
        future_model = trained_until is not None and s.cutoff < utc(trained_until)
        # Fitted observations are ETB small-business owners, not every relative,
        # employee or account. Do not silently generalize beyond that population.
        model_population = (subject.startswith("Person:") and f.income is not None
                            and network_summary["active_owned_businesses"] > 0)
        model_available = not s.truncated and not future_model and model_population
        anomaly = {"status": "unavailable", "score": None, "reason": "No trained anomaly artifact", "contributions": []}
        if self.anomaly and model_available:
            anomaly = self.anomaly.predict(f)
        if anomaly.get("flagged"):
            contributing = [c for c in anomaly["contributions"] if c["score_contribution"] > 0]
            ids = sorted({tid for c in contributing for tid in c["transaction_ids"]})
            leads.append(Lead("BEHAVIORAL_DEVIATION", "anomaly", "Several behavioral measurements depart from the training-normal reference and the subject's own prior history.",
                              anomaly["score"], ids, measurements={"contributions": contributing, "baseline": "train-normal robust median/MAD"}))
        gnn = {"status": "unavailable", "score": None, "reason": "No trained GNN artifact", "attributions": []}
        if future_model:
            anomaly = {"status": "unavailable", "score": None, "reason": "Model was trained after the requested cutoff", "contributions": []}
            gnn["reason"] = "Model was trained after the requested cutoff"
        elif not model_population:
            anomaly["reason"] = gnn["reason"] = "Subject is outside the trained ETB business-owner population"
        elif s.truncated:
            anomaly["reason"] = gnn["reason"] = "Neighborhood was truncated"
        if self.gnn and model_available and has_graph_activity:
            sample = graph_sample(s)
            score = self.gnn.predict(sample)
            attributions = self.gnn.explain(sample) if score >= self.config["gnn"]["threshold"] else []
            gnn = {"status": "available", "score": score, "flagged": score >= self.config["gnn"]["threshold"],
                   "reason": "Learned synthetic observed-scenario affinity; not calibrated fraud probability", "attributions": attributions}
            if gnn["flagged"]:
                ids = sorted({tid for item in attributions for tid in item["transaction_ids"]})
                leads.append(Lead("LEARNED_GRAPH_AFFINITY", "gnn", "The learned graph representation resembles the synthetic suspicious training class. Edge-removal sensitivity is explanatory context, not proof of misconduct.",
                                  score, ids, measurements={"edge_ablation": attributions, "model_version": self.gnn.VERSION,
                                  "model_input_features": list(NODE_FEATURES)}, highlight=bool(attributions)))
        evidence = build_evidence(s, leads, graph, self.dataset.version, self.dataset.checksum, self.fingerprint)
        graph["analysis_fingerprint"] = self.fingerprint

        def component(name, strength, reason, available=True, confidence=.8):
            return {"name": name, "status": "available" if available else "unavailable", "strength": strength if available else None,
                    "confidence": confidence if available else 0., "reason": reason,
                    "evidence_ids": [e["evidence_id"] for e in evidence if e["signal_source"] == name]}

        complete = not s.truncated
        components = {
            "rules": component("rules", max((lead.strength for lead in rules), default=0.), "Explicit checks over cutoff-valid source facts", complete and has_graph_activity, .9),
            "network": component("network", max((lead.strength for lead in network), default=0.), "Temporal circular paths and active family/business context", complete and not network_summary["search_truncated"] and has_graph_activity, .9),
            "anomaly": component("anomaly", anomaly["score"], anomaly["reason"], anomaly["status"] == "available", .6),
            "gnn": component("gnn", gnn["score"], gnn["reason"], gnn["status"] == "available", .5),
        }
        limitations = ["Synthetic development benchmark; Phase 3 metrics do not establish real-world performance.",
                       "Scores are investigation priorities, not fraud probabilities or guilt determinations.",
                       "No invoice evidence or full balance ledger; transaction context and declarations may require verification.",
                       "GNN edge ablation holds node features fixed and is sensitivity analysis, not causal attribution."]
        if s.truncated or network_summary["search_truncated"]:
            limitations.append("Neighborhood/path limits reached; affected components are unavailable and the graph may be incomplete.")
        if future_model:
            limitations.append("Model artifacts postdate the cutoff and were excluded.")
        return {"version": VERSION, "subject": {"entity_key": subject},
                "investigation_window": {"cutoff": s.cutoff.isoformat(), "observation_start": s.window_start.isoformat(), "history_start": s.history_start.isoformat()},
                "assessment": fuse(components, self.config["fusion"]), "intelligence_components": components,
                "findings": {"rules": [asdict(lead) for lead in rules], "rule_checks": checks, "network": [asdict(lead) for lead in network],
                             "network_context": network_summary, "anomaly": anomaly, "gnn": gnn},
                "features": f.values, "evidence": evidence, "graph": annotate_graph(graph, evidence), "limitations": limitations,
                "provenance": {"dataset_version": self.dataset.version, "source_manifest_sha256": self.dataset.checksum,
                               "analysis_fingerprint": self.fingerprint,
                               "model_training": {k: v for k, v in self.model_provenance.items() if k not in {"training_ground_truth_ids", "training_subjects"}},
                               "future_events_excluded": True, "ground_truth_used_at_inference": False}}

    def rank(self, subjects, cutoff, top_n=None):
        count = self.config["top_n"] if top_n is None else top_n
        if type(count) is not int or count < 1:
            raise ValueError("top_n must be a positive integer")
        results = [self.investigate(key, cutoff) for key in sorted(set(subjects))]
        return rank_results(results, count)


def rank_results(results, top_n):
    eligible = [r for r in results if r["assessment"]["strength"] is not None]
    ordered = sorted(eligible, key=lambda r: (-r["assessment"]["strength"], r["subject"]["entity_key"]))[:top_n]
    return [{"rank": i+1, "entity_key": r["subject"]["entity_key"], "cutoff": r["investigation_window"]["cutoff"],
             "dataset_version": r["provenance"]["dataset_version"], "analysis_fingerprint": r["provenance"]["analysis_fingerprint"],
             "overall_risk": r["assessment"]["strength"], "risk_level": r["assessment"]["risk_level"],
             "is_fraud_probability": False, "score_breakdown": r["assessment"]["breakdown"],
             "evidence_ids": [e["evidence_id"] for e in r["evidence"]]} for i, r in enumerate(ordered)]
