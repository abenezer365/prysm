"""Stable intelligence-layer output contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuleFinding:
    rule_id: str
    rule_name: str
    status: str
    severity: str
    score: float
    explanation: str
    entity_ids: list[str]
    transaction_ids: list[str] = field(default_factory=list)
    measurements: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnomalyPrediction:
    entity_key: str
    as_of: str
    anomaly_score: float
    is_anomaly: bool
    model_version: str = "numpy-isolation-forest-v1"


@dataclass(frozen=True)
class ModelPrediction:
    entity_key: str
    as_of: str
    probability: float
    predicted_label: bool
    model_version: str = "numpy-logistic-v1"


@dataclass(frozen=True)
class EvaluationResult:
    component: str
    split: str
    metrics: dict[str, Any]


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    entity_id: str
    signal_source: str
    signal_type: str
    description: str
    severity: str
    confidence: float
    supporting_entity_ids: list[str] = field(default_factory=list)
    supporting_transaction_ids: list[str] = field(default_factory=list)
    supporting_relationship_ids: list[str] = field(default_factory=list)
    supporting_edge_ids: list[str] = field(default_factory=list)
    measurements: dict[str, Any] = field(default_factory=dict)
    timestamps: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignalComponent:
    name: str
    status: str
    strength: float | None
    confidence: float
    reason: str
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InvestigationResult:
    investigation_id: str
    subject: dict[str, Any]
    investigation_window: dict[str, Any]
    graph_summary: dict[str, Any]
    intelligence_components: dict[str, Any]
    assessment: dict[str, Any]
    confidence: dict[str, Any]
    findings: dict[str, Any]
    evidence: list[dict[str, Any]]
    limitations: list[str]
    provenance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
