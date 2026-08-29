from __future__ import annotations
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import pandas as pd
from prysm_ai.investigation import InvestigationEngine
from .schemas import AnalyzeResponse, Assessment, InvestigationContext

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
