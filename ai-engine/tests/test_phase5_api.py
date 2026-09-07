import importlib.util
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

spec = importlib.util.spec_from_file_location('phase5_http', Path(__file__).resolve().parents[1] / 'api/intelligence.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('AI_ENGINE_API_KEY', 'phase5-test-key')
    return TestClient(api.app)

def test_internal_auth_fails_closed(client, monkeypatch):
    assert client.get('/ready').status_code == 401
    monkeypatch.delenv('AI_ENGINE_API_KEY')
    assert client.get('/ready').status_code == 503

def test_current_engine_result_and_search(client, monkeypatch):
    headers = {'Authorization': 'Bearer phase5-test-key'}
    assert client.get('/ready', headers=headers).status_code == 200
    monkeypatch.setenv(
        'PRYSM_MODELS',
        str(Path(__file__).resolve().parents[1] / 'runs' / 'demo-v2-build' / 'model_bundle.json'),
    )
    persisted = client.get('/v2/rank/persisted?limit=10', headers=headers)
    assert persisted.status_code == 200
    assert len(persisted.json()['ranking']) == 10
    assert len({row['entity_key'] for row in persisted.json()['ranking']}) == 10
    assert all(row['display_label'] for row in persisted.json()['ranking'])
    assert persisted.json()['cutoff'].endswith('+00:00')
    result = client.post('/v2/investigate', headers=headers, json={'subject': 'Person:P01870', 'cutoff': '2025-12-11T10:00:00Z'})
    assert result.status_code == 200
    facts = result.json()
    assert facts['version'] == 'prysm-intelligence-v2'
    assert facts['provenance']['ground_truth_used_at_inference'] is False
    assert facts['graph']['analysis_fingerprint'] == facts['provenance']['analysis_fingerprint']
    assert facts['evidence']
    found = client.get('/v2/people/search?q=P01870', headers=headers).json()
    assert found['data'][0]['externalRef'] == 'Person:P01870'
    assert found['data'][0]['label'] != 'Person:P01870'
    assert found['data'][0]['analysisCutoffAt'] == '2025-12-04T11:00:00+00:00'
    derived = client.post('/v2/investigate', headers=headers, json={
        'subject': found['data'][0]['externalRef'],
        'cutoff': found['data'][0]['analysisCutoffAt'],
    }).json()
    assert derived['assessment']['risk_level'] == 'moderate'
    assert derived['assessment']['strength'] == facts['assessment']['strength']

    control = client.get('/v2/people/search?q=Bekele%20Yonas', headers=headers).json()
    control_person = next(row for row in control['data'] if row['externalRef'] == 'Person:P01710')
    assert control_person['analysisCutoffAt'] == '2025-12-09T10:00:00+00:00'
    control_result = client.post('/v2/investigate', headers=headers, json={
        'subject': control_person['externalRef'],
        'cutoff': control_person['analysisCutoffAt'],
    }).json()
    assert control_result['assessment']['risk_level'] == 'low'
    assert control_result['assessment']['strength'] < .35

    birtukan = client.get('/v2/people/search?q=Birtukan%20Abebe', headers=headers).json()
    suspicious_person = next(row for row in birtukan['data'] if row['externalRef'] == 'Person:P00640')
    suspicious_result = client.post('/v2/investigate', headers=headers, json={
        'subject': suspicious_person['externalRef'],
        'cutoff': suspicious_person['analysisCutoffAt'],
    }).json()
    assert suspicious_result['assessment']['risk_level'] == 'moderate'
    assert suspicious_result['assessment']['strength'] >= .35

@pytest.mark.parametrize('body', [
    {'subject': 'Person:P01870', 'cutoff': '2025-12-11'},
    {'subject': 'Person:P01870', 'cutoff': '2025-12-11T10:00:00Z', 'evidence': []},
])
def test_invalid_requests(client, body):
    assert client.post('/v2/investigate', headers={'Authorization': 'Bearer phase5-test-key'}, json=body).status_code == 422

def test_missing_subject(client):
    assert client.post('/v2/investigate', headers={'Authorization': 'Bearer phase5-test-key'}, json={'subject': 'Person:missing', 'cutoff': '2025-12-11T10:00:00Z'}).status_code == 404
