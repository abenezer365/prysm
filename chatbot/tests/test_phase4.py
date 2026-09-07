import json
from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient
import pytest
import requests

from main import app, service

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[2]


def headers(monkeypatch):
    monkeypatch.setenv("RAG_API_KEY", "phase4-test")
    return {"Authorization": "Bearer phase4-test"}


def real_result():
    # A real Phase 3 investigation retained in the prior measured ranking.
    path = ROOT / "ai-engine/runs/evaluation-v3/test_results.jsonl"
    if path.exists():
        return next(r for line in path.read_text().splitlines() if (r := json.loads(line))["evidence"])
    return json.loads((ROOT / "ai-engine/examples/phase2_investigation.json").read_text())


def test_real_evidence_is_preserved_and_input_not_mutated(monkeypatch):
    facts = real_result()
    before = deepcopy(facts)
    response = client.post("/explain", headers=headers(monkeypatch), json={"intelligence": facts})
    assert response.status_code == 200
    result = response.json()
    assert result["detected"]["evidence"] == facts["evidence"]
    assert result["detected"]["assessment"] == facts["assessment"]
    assert facts == before
    assert result["provenance"]["provider"] == "local_extract"
    assert result["explanation"]["knowledge_context"]


def test_private_facts_and_question_never_enter_gemini(monkeypatch):
    facts = real_result()
    service.key_manager.keys = ["fake-test-key"]
    sent = []
    def post(url, **kwargs):
        sent.append(json.dumps(kwargs["json"]))
        assert "key=" not in url
        assert kwargs["headers"]["x-goog-api-key"] == "fake-test-key"
        assert kwargs["allow_redirects"] is False
        class Response:
            status_code = 200
            def json(self):
                # Reference selection, never invented case prose.
                context = sent[-1]
                key = next(d["id"] for d in service.store.documents if d["id"].startswith("prysm-method-") and d["id"] in context)
                return {"candidates": [{"content": {"parts": [{"text": json.dumps({"knowledge_ids": [key]})}]}}]}
        return Response()
    monkeypatch.setattr(requests, "post", post)
    response = client.post("/explain", headers=headers(monkeypatch), json={"intelligence": facts, "question": "PRIVATE_SENTINEL bank account 1234"})
    assert response.status_code == 200
    assert response.json()["provenance"]["provider"] == "gemini_reference_selection"
    assert sent
    for payload in sent:
        assert "PRIVATE_SENTINEL" not in payload
        assert facts["subject"]["entity_key"] not in payload
        for evidence in facts["evidence"]:
            assert evidence["evidence_id"] not in payload


@pytest.mark.parametrize("output", ['{"knowledge_ids":["invented"]}', 'not-json', '{"knowledge_ids":[],"finding":"guilty"}'])
def test_unsupported_provider_output_falls_back(monkeypatch, output):
    service.key_manager.keys = ["fake"]
    monkeypatch.setattr(service.llm, "generate", lambda *a, **kw: output)
    response = client.post("/explain", headers=headers(monkeypatch), json={"intelligence": real_result()})
    assert response.status_code == 200
    assert response.json()["provenance"]["provider"] == "local_extract_after_provider_failure"
    assert "guilty" not in response.text


def test_auth_and_mixed_analysis_rejected(monkeypatch):
    auth = headers(monkeypatch)
    assert client.post("/explain", json={"intelligence": real_result()}).status_code == 401
    facts = real_result()
    facts["evidence"][0]["provenance"]["analysis_fingerprint"] = "other"
    assert client.post("/explain", headers=auth, json={"intelligence": facts}).status_code == 422


def test_legacy_investigator_never_calls_cloud(monkeypatch):
    def forbidden(*a, **k):
        raise AssertionError("Private cloud request")
    monkeypatch.setattr(service.llm, "generate", forbidden)
    response = client.post("/ask", headers=headers(monkeypatch), json={"message": "Why?", "authenticated": True, "context": {"summary": "A supplied signal needs review."}})
    assert response.status_code == 200
    assert "supplied signal" in response.json()["answer"]


def test_ingestion_provenance_and_operational_record_rejection(monkeypatch):
    auth = headers(monkeypatch)
    assert client.post("/ingest", headers=auth, json={"title": "case", "content": '{"evidence_id":"EVD:1"}'}).status_code == 422
    created = client.post("/ingest", headers=auth, json={"title": "General guidance", "content": "Check timestamp quality.", "source": "reviewed handbook"}).json()
    doc = next(d for d in client.get("/documents", headers=auth).json()["data"] if d["id"] == created["documentId"])
    assert doc["createdAt"] and doc["updatedAt"] and len(doc["content_sha256"]) == 64


def test_timeout_is_bounded_and_falls_back(monkeypatch):
    service.key_manager.keys = ["fake"]
    calls = []
    def timeout(*args, **kwargs):
        calls.append(kwargs["timeout"])
        raise requests.Timeout()
    monkeypatch.setattr(requests, "post", timeout)
    result = client.post("/explain", headers=headers(monkeypatch), json={"intelligence": real_result()})
    assert result.status_code == 200
    assert 1 <= len(calls) <= 2
    assert result.json()["provenance"]["provider"] == "local_extract_after_provider_failure"


def test_all_saved_phase3_test_results(monkeypatch):
    path = ROOT / "ai-engine/runs/evaluation-v3/test_results.jsonl"
    if not path.exists():
        pytest.skip("Full local Phase 3 run not present; portable Phase 2 example tested separately")
    auth = headers(monkeypatch)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(rows) == 80
    types, empty = set(), 0
    for facts in rows:
        response = client.post("/explain", headers=auth, json={"intelligence": facts})
        assert response.status_code == 200
        result = response.json()
        assert result["detected"]["evidence"] == facts["evidence"]
        assert result["detected"]["assessment"] == facts["assessment"]
        types.update(e["signal_type"] for e in facts["evidence"])
        if not facts["evidence"]:
            empty += 1
            assert not result["explanation"]["findings"]
            assert "No supported finding" in result["summary"]
    assert empty > 0
    assert {"STRUCTURED_DEPOSITS", "HIGH_VELOCITY", "UNEXPLAINED_AMOUNT", "IMPOSSIBLE_BRANCH_TRAVEL",
            "BUSINESS_RECEIPTS_MISMATCH", "NEW_DEVICE_RAPID_OUTFLOW", "RAPID_CIRCULAR_FLOW", "FAMILY_PASS_THROUGH"} <= types
