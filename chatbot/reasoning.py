"""Local evidence rendering + bounded, general-knowledge Gemini assistance.

No detector, conversation database or local-model download lives here.
Cloud output selects references; it cannot write or change case facts.
"""
from copy import deepcopy
import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


TOPICS = {
    "STRUCTURED_DEPOSITS": "structuring",
    "HIGH_VELOCITY": "velocity",
    "UNEXPLAINED_AMOUNT": "amount",
    "IMPOSSIBLE_BRANCH_TRAVEL": "geography",
    "BUSINESS_RECEIPTS_MISMATCH": "tax",
    "NEW_DEVICE_RAPID_OUTFLOW": "theft",
    "RAPID_CIRCULAR_FLOW": "network",
    "FAMILY_PASS_THROUGH": "family",
    "BEHAVIORAL_DEVIATION": "anomaly",
    "LEARNED_GRAPH_AFFINITY": "graph",
}


class IntelligenceContext(BaseModel):
    version: Literal["prysm-intelligence-v2"]
    subject: dict[str, Any]
    assessment: dict[str, Any]
    evidence: list[dict[str, Any]] = Field(max_length=100)
    provenance: dict[str, Any]
    limitations: list[str] = Field(default_factory=list, max_length=50)

    @model_validator(mode="after")
    def validate_evidence(self):
        if len(json.dumps(self.model_dump(), allow_nan=False)) > 250_000:
            raise ValueError("Intelligence context exceeds 250 KB")
        fingerprint = self.provenance.get("analysis_fingerprint")
        if not isinstance(fingerprint, str) or not fingerprint or not isinstance(self.subject.get("entity_key"), str):
            raise ValueError("Subject and analysis fingerprint are required")
        score = self.assessment.get("strength")
        if score is not None and (type(score) not in (int, float) or not 0 <= score <= 1):
            raise ValueError("Invalid attention score")
        if self.assessment.get("is_fraud_probability") is not False:
            raise ValueError("Expected uncalibrated intelligence assessment")
        ids = set()
        for item in self.evidence:
            eid = item.get("evidence_id")
            if not isinstance(eid, str) or not eid or eid in ids:
                raise ValueError("Evidence IDs must be unique and nonempty")
            ids.add(eid)
            if not isinstance(item.get("description"), str) or not isinstance(item.get("signal_type"), str):
                raise ValueError("Evidence requires description and signal type")
            if not isinstance(item.get("provenance"), dict) or item["provenance"].get("analysis_fingerprint") != fingerprint:
                raise ValueError("Evidence belongs to a different analysis")
        return self


class ExplainRequest(BaseModel):
    intelligence: IntelligenceContext
    question: str = Field(default="Explain the supplied findings and next review steps.", min_length=1, max_length=2000)


class GuidanceSelection(BaseModel):
    model_config = {"extra": "forbid"}
    knowledge_ids: list[str] = Field(max_length=3)


def explain(request: ExplainRequest, store, llm):
    facts = request.intelligence
    topics = sorted({TOPICS[e["signal_type"]] for e in facts.evidence if e["signal_type"] in TOPICS})
    # Both private question and evidence stay local. Only an allowlisted topic
    # and curated, explicitly cloud-approved methodology can leave this process.
    query = " ".join(topics) or "investigator guidance"
    documents = store.search(query, limit=3)
    references = [{"id": d["id"], "title": d["title"], "source": d["source"], "version": d["version"],
                   "content": d["content"][:1800], "content_sha256": hashlib.sha256(d["content"].encode()).hexdigest(),
                   "createdAt": d.get("createdAt"), "updatedAt": d.get("updatedAt")} for d in documents]
    approved = [r for r, d in zip(references, documents) if d.get("metadata", {}).get("cloud_approved") is True]
    selected_ids, provider = [r["id"] for r in references], "local_extract"
    if approved and llm.key_manager.keys:
        prompt_context = json.dumps({"topics": topics, "references": approved}, sort_keys=True)
        raw = llm.generate("Select up to three useful methodology reference IDs. Return only JSON with knowledge_ids, no prose or extra fields.",
                           prompt_context, mode="knowledge_selection", structured=True)
        try:
            selection = GuidanceSelection.model_validate_json(raw)
            allowed = {r["id"] for r in approved}
            if not selection.knowledge_ids or not set(selection.knowledge_ids) <= allowed or len(set(selection.knowledge_ids)) != len(selection.knowledge_ids):
                raise ValueError("Unsupported knowledge citation")
            selected_ids, provider = selection.knowledge_ids, "gemini_reference_selection"
        except ValueError:
            provider = "local_extract_after_provider_failure"
    by_id = {r["id"]: r for r in references}
    guidance = [by_id[key] for key in selected_ids]
    findings = [{"evidence_id": e["evidence_id"], "detector": e.get("signal_source"), "finding": e["signal_type"],
                 "reasoning": e["description"], "transaction_ids": e.get("supporting_transaction_ids", []),
                 "relationship_ids": e.get("supporting_relationship_ids", []), "entity_ids": e.get("supporting_entity_ids", [])}
                for e in facts.evidence]
    score = facts.assessment.get("strength")
    summary = (f"{facts.subject['entity_key']}: {len(findings)} evidence-backed lead(s); "
               f"attention score {score if score is not None else 'unavailable'}. "
               "Review the cited evidence; this is not a fraud verdict.")
    if not findings:
        summary += " No supported finding was supplied; absence of a finding does not establish innocence."
    return {"version": "prysm-reasoning-v1", "summary": summary,
            "detected": {"subject": deepcopy(facts.subject), "assessment": deepcopy(facts.assessment), "evidence": deepcopy(facts.evidence)},
            "explanation": {"findings": findings, "knowledge_context": guidance,
                            "uncertainty": list(dict.fromkeys([*facts.limitations, "Knowledge explains methodology, not facts about this subject.",
                                                               "Gemini selects general references only; case reasoning is a local extract of detector evidence."])),
                            "recommended_direction": "Verify the cited source records, transaction purpose and relationship validity before drawing conclusions."},
            "provenance": {"analysis_fingerprint": facts.provenance["analysis_fingerprint"], "provider": provider,
                           "retrieval_query": query, "retrieved_ids": [r["id"] for r in references],
                           "private_context_sent_to_cloud": False, "cloud_scope": "allowlisted topics and cloud-approved general knowledge only",
                           "local_llm": "deferred_by_request", "conversation_retained": False}}
