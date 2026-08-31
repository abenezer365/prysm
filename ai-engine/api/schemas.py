from __future__ import annotations
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

class SubjectContext(BaseModel):
    id: str
    type: str
    label: str
    externalRef: str | None = None

class GraphContext(BaseModel):
    nodes: list[dict[str, Any]] = Field(default_factory=list, max_items=250)
    edges: list[dict[str, Any]] = Field(default_factory=list, max_items=2000)
    truncated: bool = False

class ProvenanceContext(BaseModel):
    futureEventsExcluded: Literal[True]
    graphDepth: int = Field(ge=1, le=3)
    maxNodes: int = Field(ge=1, le=250)

class InvestigationContext(BaseModel):
    class Config:
        extra = "forbid"
    version: Literal["prysm-investigation-context-v1"]
    requestId: str
    investigationId: str
    subject: SubjectContext
    cutoffAt: datetime
    lookbackStart: datetime
    dataSnapshot: str
    transactions: list[dict[str, Any]] = Field(default_factory=list, max_items=1000)
    graph: GraphContext
    provenance: ProvenanceContext
    graphSnapshotId: str | None = None

class Assessment(BaseModel):
    type: Literal["uncalibrated_attention_assessment"]
    strength: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    isFraudProbability: Literal[False] = False

class AnalyzeResponse(BaseModel):
    requestId: str
    investigationId: str
    engineVersion: str
    generatedAt: datetime
    assessment: Assessment
    components: dict[str, Any]
    findings: dict[str, Any]
    evidence: list[dict[str, Any]]
    graphIntelligence: dict[str, Any]
    limitations: list[str]
    modelVersions: dict[str, Any]
    provenance: dict[str, Any]

class PersonSearchResult(BaseModel):
    externalRef: str
    label: str
    status: str | None = None
    profile: dict[str, Any] = Field(default_factory=dict)

class PersonSearchResponse(BaseModel):
    data: list[PersonSearchResult]
    total: int
    datasetVersion: str
