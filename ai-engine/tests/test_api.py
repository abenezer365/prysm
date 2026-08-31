from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)
def test_health_is_lightweight():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "prysm-ai-engine"

def test_ready_reports_real_artifacts():
    response = client.get("/ready")
    assert response.status_code == 200
    assert all(value == "ready" for value in response.json()["models"].values())

def test_analysis_rejects_noncanonical_subject_before_inference():
    payload = {"version":"prysm-investigation-context-v1","requestId":"r","investigationId":"i","subject":{"id":"x","type":"Person","label":"safe"},"cutoffAt":"2025-01-01T00:00:00Z","lookbackStart":"2024-01-01T00:00:00Z","dataSnapshot":"test","transactions":[],"graph":{"nodes":[],"edges":[],"truncated":False},"provenance":{"futureEventsExcluded":True,"graphDepth":2,"maxNodes":100}}
    response = client.post("/v1/analyze", json=payload)
    assert response.status_code == 422

def test_api_key_is_required_when_configured(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_API_KEY", "internal-test-key")
    response = client.post("/v1/analyze", json={})
    assert response.status_code == 401

def test_real_existing_engine_analysis_through_http_boundary():
    payload = {"version":"prysm-investigation-context-v1","requestId":"pytest-real","investigationId":"00000000-0000-4000-8000-000000000001","subject":{"id":"00000000-0000-4000-8000-000000000002","type":"Company","label":"Company:C04166","externalRef":"Company:C04166"},"cutoffAt":"2025-06-16T00:00:00Z","lookbackStart":"2024-06-16T00:00:00Z","dataSnapshot":"pytest","transactions":[],"graph":{"nodes":[],"edges":[],"truncated":False},"provenance":{"futureEventsExcluded":True,"graphDepth":3,"maxNodes":250}}
    response = client.post("/v1/analyze", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["assessment"]["type"] == "uncalibrated_attention_assessment"
    assert body["assessment"]["isFraudProbability"] is False
    assert body["graphIntelligence"]["cutoffSafe"] is True
    assert body["evidence"]

def test_full_dataset_person_search_and_unaligned_person_investigation():
    search = client.get("/v1/people/search", params={"q": "P000001", "limit": 5})
    assert search.status_code == 200
    person = search.json()["data"][0]
    assert person["externalRef"] == "Person:P000001"
    payload = {"version":"prysm-investigation-context-v1","requestId":"pytest-universal","investigationId":"00000000-0000-4000-8000-000000000003","subject":{"id":"00000000-0000-4000-8000-000000000004","type":"Person","label":person["label"],"externalRef":person["externalRef"]},"cutoffAt":"2025-12-31T23:59:59Z","lookbackStart":"2024-12-31T23:59:59Z","dataSnapshot":"pytest-full-dataset","transactions":[],"graph":{"nodes":[],"edges":[],"truncated":False},"provenance":{"futureEventsExcluded":True,"graphDepth":3,"maxNodes":250}}
    response = client.post("/v1/analyze", json=payload)
    assert response.status_code == 200
    components = response.json()["components"]
    assert components["graph"]["status"] == "available"
    assert components["gnn"]["status"] == "available"
    assert components["transaction"]["status"] == "available"
    assert response.json()["assessment"]["isFraudProbability"] is False

    graph = client.get("/v1/graph/Person:P000001", params={"cutoffAt":"2025-12-31T23:59:59Z","maxHops":2,"maxNodes":100})
    assert graph.status_code == 200
    body = graph.json()
    assert any(node["isSubject"] for node in body["nodes"])
    assert all(edge["source"] and edge["target"] and edge["label"] for edge in body["edges"])
