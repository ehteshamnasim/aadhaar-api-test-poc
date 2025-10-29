"""AI-Generated Tests v66 - 2025-10-29 21:02:20"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()


def test_face_authentication_missing_fields(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 401


def test_face_authentication_success(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'aadhaar_number': '123456789012', 'face_image': 'base64image'})
    assert response.status_code == 200


def test_generate_otp_missing_fields(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400


def test_generate_otp_success(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200


def test_get_demographics_missing_fields(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400


def test_get_demographics_no_consent(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': False})
    assert response.status_code == 403


def test_get_demographics_success(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 200


def test_get_masked_aadhaar_failure(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar', headers={'Authorization': 'invalid'})
    assert response.status_code == 400


def test_get_masked_aadhaar_success(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 200


def test_health_check_failure(client):
    response = client.get('/api/v1/aadhaar/health-check', headers={'Authorization': 'invalid'})
    assert response.status_code == 503

def test_health_check_success(client):
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 200


def test_perform_ekyc_missing_fields(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400


def test_perform_ekyc_no_consent(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '123456', 'consent': False})
    assert response.status_code == 403


def test_perform_ekyc_success(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '123456', 'consent': True})
    assert response.status_code == 200


def test_test_new_endpoint_success(client):
    response = client.get('/api/v1/aadhaar/test-new-endpoint')
    assert response.status_code == 200


def test_verify_aadhaar_invalid_captcha(client):
    response = client.post('/api/v1/aadhaar/verify', json={'aadhaar_number': '123456789012', 'captcha': 'invalid'})
    assert response.status_code == 401


def test_verify_aadhaar_missing_fields(client):
    response = client.post('/api/v1/aadhaar/verify', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400


def test_verify_aadhaar_success(client):
    response = client.post('/api/v1/aadhaar/verify', json={'aadhaar_number': '123456789012', 'captcha': 'abc123'})
    assert response.status_code == 200


def test_verify_otp_missing_fields(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '123456'})
    assert response.status_code == 400


def test_verify_otp_success(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '123456', 'otp': '123456'})
    assert response.status_code == 200

