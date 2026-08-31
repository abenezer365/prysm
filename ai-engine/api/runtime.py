from __future__ import annotations
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import pandas as pd
from prysm_ai.investigation import InvestigationEngine
from .schemas import AnalyzeResponse, Assessment, InvestigationContext, PersonSearchResponse

ENGINE_VERSION = "prysm-ai-http-v1"

class EngineRuntime:
    def __init__(self) -> None:
        project = Path(__file__).resolve().parents[1]
        configured = os.getenv("PRYSM_AI_ARTIFACT_ROOT", "runs/scenario-v1")
        root = Path(configured)
        self.root = root if root.is_absolute() else project / root
        self.config_path = self.root / "config" / "intelligence.json"
        self.required = {
            "rules": self.root / "signals" / "rule_findings.jsonl",
            "anomaly": self.root / "artifacts" / "anomaly_model.json",
            "supervised": self.root / "artifacts" / "supervised_model.json",
            "gnn": self.root / "artifacts" / "gnn_encoder.json",
            "graph": self.root / "graph" / "MANIFEST.json",
        }
        self._engine: InvestigationEngine | None = None
        self._persons: pd.DataFrame | None = None
        self._lock = threading.Lock()

    def state(self) -> dict[str, Any]:
        models = {name: "ready" if path.is_file() else "unavailable" for name, path in self.required.items()}
        return {"status": "ready" if all(v == "ready" for v in models.values()) and self.config_path.is_file() else "degraded", "service": "prysm-ai-engine", "artifactRoot": str(self.root), "models": models}

    def engine(self) -> InvestigationEngine:
        if self._engine is None:
            with self._lock:
                if self._engine is None:
                    config = json.loads(self.config_path.read_text(encoding="utf-8"))
                    self._engine = InvestigationEngine(self.root, config)
        return self._engine

    def search_people(self, query: str, limit: int) -> PersonSearchResponse:
        if self._persons is None:
            path = self.root / "data" / "processed" / "persons.parquet"
            columns = ["person_id", "first_name", "last_name", "date_of_birth", "nationality", "occupation", "employment_status", "city", "region", "country"]
            people = pd.read_parquet(path, columns=columns).copy()
            people["label"] = (people.first_name.fillna("").astype(str) + " " + people.last_name.fillna("").astype(str)).str.strip()
            people["search"] = (people.person_id.astype(str) + " " + people.label).str.casefold()
            self._persons = people
        needle = query.strip().casefold()
        matches = self._persons[self._persons.search.str.contains(needle, regex=False, na=False)].head(limit)
        data = []
        for row in matches.itertuples():
            data.append({"externalRef": f"Person:{row.person_id}", "label": row.label or str(row.person_id), "status": None if pd.isna(row.employment_status) else str(row.employment_status), "profile": {"fullName": row.label or None, "dateOfBirth": None if pd.isna(row.date_of_birth) else pd.Timestamp(row.date_of_birth).date().isoformat(), "nationality": None if pd.isna(row.nationality) else str(row.nationality), "occupation": None if pd.isna(row.occupation) else str(row.occupation), "employmentStatus": None if pd.isna(row.employment_status) else str(row.employment_status), "city": None if pd.isna(row.city) else str(row.city), "region": None if pd.isna(row.region) else str(row.region), "country": None if pd.isna(row.country) else str(row.country)}})
        return PersonSearchResponse(data=data, total=len(data), datasetVersion="prysm-scenario-v1")

    def graph(self, subject: str, cutoff: pd.Timestamp, max_hops: int, max_nodes: int) -> dict[str, Any]:
        engine = self.engine()
        nodes, edges = engine.graph_store.subgraph(subject, cutoff, max_hops, max_nodes, 365, "predictive", None, 0.3)
        people = self._persons
        if people is None:
            self.search_people("__index_warmup__", 1)
            people = self._persons
        person_labels = dict(zip(("Person:" + people.person_id.astype(str)), people.label.astype(str)))
        raw_root = Path(__file__).resolve().parents[2] / "data" / "raw"
        companies_path, banks_path = raw_root / "companies.parquet", raw_root / "banks.parquet"
        companies = pd.read_parquet(companies_path, columns=["company_id", "company_name"]) if companies_path.is_file() else pd.DataFrame()
        banks = pd.read_parquet(banks_path, columns=["institution_id", "institution_name"]) if banks_path.is_file() else pd.DataFrame()
        company_labels = {} if companies.empty else dict(zip("Company:" + companies.company_id.astype(str), companies.company_name.astype(str)))
        bank_labels = {} if banks.empty else dict(zip("Bank:" + banks.institution_id.astype(str), banks.institution_name.astype(str)))
        labels = {**person_labels, **company_labels, **bank_labels}
        node_data = []
        for row in nodes.itertuples(index=False):
            key = str(row.node_key); source_id = str(row.source_id)
            label = labels.get(key) or ({"Account": "Account", "Invoice": "Invoice", "Device": "Device"}.get(str(row.node_type), str(row.node_type)) + f" {source_id}")
            node_data.append({"id": key, "externalRef": key, "sourceId": source_id, "type": str(row.node_type), "label": label, "status": None if pd.isna(row.status) else str(row.status), "isSubject": key == subject})
        edge_data = []
        for row in edges.itertuples(index=False):
            edge_data.append({"id": str(row.edge_id), "source": str(row.source_key), "target": str(row.target_key), "type": str(row.edge_type), "label": str(row.edge_type).replace("relationship:", "").replace("_", " "), "confidence": 1.0 if pd.isna(row.confidence) else float(row.confidence), "timestamp": None if pd.isna(row.event_time) else pd.Timestamp(row.event_time).isoformat(), "amountEtb": None if pd.isna(row.amount_etb) else float(row.amount_etb), "currency": None if pd.isna(row.currency) else str(row.currency), "transactionId": None if pd.isna(row.transaction_id) else str(row.transaction_id), "relationshipId": None if pd.isna(row.relationship_id) else str(row.relationship_id)})
        return {"subject": subject, "cutoffAt": cutoff.isoformat(), "maxHops": max_hops, "maxNodes": max_nodes, "truncated": len(node_data) >= max_nodes, "nodes": node_data, "edges": edge_data}

    def analyze(self, context: InvestigationContext) -> AnalyzeResponse:
        subject = context.subject.externalRef
        if not subject or ":" not in subject:
            raise ValueError("subject.externalRef must be a canonical EntityType:source_id key")
        result = self.engine().investigate(subject, pd.Timestamp(context.cutoffAt), "predictive").to_dict()
        raw_assessment = result["assessment"]
        strength = float(raw_assessment.get("assessment_strength", raw_assessment.get("strength", 0.0)))
        confidence_block = result.get("confidence", {})
        confidence = float(confidence_block.get("score", confidence_block.get("overall", confidence_block.get("confidence", 0.0))))
        graph_summary = result.get("graph_summary", {})
        return AnalyzeResponse(
            requestId=context.requestId, investigationId=context.investigationId, engineVersion=ENGINE_VERSION,
            generatedAt=datetime.now(timezone.utc),
            assessment=Assessment(type="uncalibrated_attention_assessment", strength=strength, confidence=confidence, isFraudProbability=False),
            components=result.get("intelligence_components", {}), findings=result.get("findings", {}), evidence=result.get("evidence", []),
            graphIntelligence={"available": True, "modelVersion": result.get("provenance", {}).get("gnn_version"), "graphSnapshotId": context.graphSnapshotId, "cutoffSafe": True, "summary": graph_summary, "limitations": ["Self-supervised structural representation; no supervised predictive GNN claim."]},
            limitations=result.get("limitations", []), modelVersions={"aiEngine": ENGINE_VERSION, **result.get("provenance", {})},
            provenance={"contextVersion": context.version, "dataSnapshot": context.dataSnapshot, "cutoff": context.cutoffAt.isoformat(), "futureEventsExcluded": True, "backendGraphContextReceived": {"nodes": len(context.graph.nodes), "edges": len(context.graph.edges), "truncated": context.graph.truncated}, "engineResultId": result["investigation_id"]},
        )

runtime = EngineRuntime()
