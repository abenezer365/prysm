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
