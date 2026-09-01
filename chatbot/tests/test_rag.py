import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("RAG_API_KEY", "test-internal-key")

from main import GeminiKeyManager, KnowledgeStore, app, service

client = TestClient(app)
def internal_headers():
    key = os.environ.get("RAG_API_KEY", "")
    return {"Authorization": f"Bearer {key}"} if key else {}


def test_root_describes_running_service():
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "Prysm chatbot / RAG"
    assert payload["health"] == "/health"


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "prysm-rag"


def test_public_ask_uses_knowledge_base():
    response = client.get("/ask?message=What%20is%20Prysm%20AI")
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "public"
    assert "Prysm" in payload["answer"]
    assert payload["sources"][0]["title"] == "Prysm AI Overview"
    assert not payload["answer"].startswith("Based on the retrieved knowledge")


def test_public_ask_does_not_attach_unrelated_sources():
    response = client.get("/ask?message=hello")
    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"] == []
    assert "couldn't find relevant information" in payload["answer"]


def test_builder_question_returns_canonical_names():
    response = client.get("/ask?message=Who%20built%20Prysm")
    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"][0]["title"] == "Prysm Builders"
    assert payload["answer"] == "Abenezer Zewge and Eyobed Moges built Prysm."
    assert len(payload["sources"]) == 1


def test_ingestion_rejects_conversation_dump():
    response = client.post(
        "/ingest",
        headers=internal_headers(),
        json={
            "title": "Bad paste",
            "content": "Yes. Since you want to put this into a RAG knowledge base, here is a master document.",
        },
    )
    assert response.status_code == 422


def test_ingest_and_retrieve_new_document():
    document = {
        "title": "Fraud Pattern: Test Pattern",
        "content": "Test pattern is a small anomaly pattern used in controlled evaluations for validation.",
        "source": "unit-test",
        "category": "concepts",
        "version": "1.0"
    }
    ingest = client.post("/ingest", json=document, headers=internal_headers())
    assert ingest.status_code == 200
    assert ingest.json()["success"] is True
    stored = Path(__file__).resolve().parents[1] / "rag" / "knowledge_base" / f"{ingest.json()['documentId']}.json"
    try:
        response = client.get("/ask?message=What%20is%20the%20Test%20Pattern")
        assert response.status_code == 200
        payload = response.json()
        assert "test pattern" in payload["answer"].lower()
    finally:
        stored.unlink(missing_ok=True)


def test_document_management_lists_and_disables_ingested_content():
    document = {
        "title": "Disable Test Knowledge",
        "content": "A uniquely managed knowledge document for disable behavior verification.",
        "source": "unit-test",
        "category": "management",
        "version": "1.0",
    }
    ingest = client.post("/ingest", json=document, headers=internal_headers())
    document_id = ingest.json()["documentId"]
    stored = Path(__file__).resolve().parents[1] / "rag" / "knowledge_base" / f"{document_id}.json"
    try:
        listing = client.get("/documents", headers=internal_headers())
        assert listing.status_code == 200
        assert any(item["id"] == document_id for item in listing.json()["data"])
        disabled = client.patch(f"/documents/{document_id}?enabled=false", headers=internal_headers())
        assert disabled.status_code == 200
        assert disabled.json()["enabled"] is False
        assert all(item["id"] != document_id for item in service.store.search("uniquely managed"))
    finally:
        stored.unlink(missing_ok=True)


def test_investigator_context_is_allowed_when_trusted():
    payload = {
        "message": "Why was this company flagged?",
        "authenticated": True,
        "userId": "user-123",
        "subjectId": "C04166",
        "investigationId": "investigation-9",
        "context": {
            "summary": "The rule triggered for an unusual transaction pattern.",
            "signals": ["rapid_outflow", "structuring"]
        }
    }
    response = client.post("/ask", json=payload, headers=internal_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "investigator"
    assert "rapid" in body["answer"].lower() or "signal" in body["answer"].lower()


def test_gemini_key_rotation_uses_next_key():
    original = os.environ.get("GOOGLE_API_KEYS")
    os.environ["GOOGLE_API_KEYS"] = "key-1,key-2,key-3"
    os.environ["GEMINI_MODELS"] = "model-a,model-b"
    try:
        manager = GeminiKeyManager()
        assert manager.active_key == "key-1"
        assert manager.active_model == "model-a"
        assert manager.rotate_key() == "key-2"
        assert manager.active_key == "key-2"
        assert manager.active_model == "model-b"
    finally:
        if original is None:
            os.environ.pop("GOOGLE_API_KEYS", None)
        else:
            os.environ["GOOGLE_API_KEYS"] = original
        os.environ.pop("GEMINI_MODELS", None)


def test_local_retrieval_prefers_exact_document_match():
    store = KnowledgeStore(Path(__file__).resolve().parent / "tmp_kb")
    store.documents = []
    store.add_document({"title": "Rapid Outflow", "content": "Rapid outflow means funds move quickly away from an account.", "source": "methodology", "category": "concepts", "version": "1.0"}, persist=False)
    store.add_document({"title": "Investigator Guidance", "content": "Use evidence and human judgment in investigations.", "source": "guidance", "category": "limitations", "version": "1.0"}, persist=False)
    results = store.search("What is Rapid Outflow")
    assert results[0]["title"] == "Rapid Outflow"

def test_internal_routes_reject_missing_key_when_configured(monkeypatch):
    monkeypatch.setenv("RAG_API_KEY", "internal-secret")
    assert client.post("/ask", json={"message": "x", "authenticated": True}).status_code == 401
    assert client.post("/ingest", json={"title": "x", "content": "y"}).status_code == 401

def test_websocket_chat_uses_existing_rag():
    key = os.environ.get("RAG_API_KEY", "")
    suffix = f"?api_key={key}" if key else ""
    with client.websocket_connect(f"/ws/chat{suffix}") as websocket:
        websocket.send_json({"message": "What is Prysm AI", "authenticated": False})
        token = websocket.receive_json(); done = websocket.receive_json()
        assert token["type"] == "token"
        assert done["type"] == "done"
        assert done["sources"]
