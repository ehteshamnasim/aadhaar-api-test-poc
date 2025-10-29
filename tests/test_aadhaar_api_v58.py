"""AI-Generated Tests v58 - 2025-10-29 19:06:10"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()


def test_face_authentication_missing_field(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={})
    assert response.status_code == 401





def test_face_authentication_success(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'aadhaar_number': '123456789012', 'face_image': 'base64image'})
    assert response.status_code == 200






def test_generate_otp_missing_field(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400






def test_generate_otp_success(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200






def test_get_demographics_missing_field(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400






def test_get_demographics_success(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 200






def test_get_masked_aadhaar_success(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 200






def test_health_check_service_unavailable(client, monkeypatch):
    """
    Test the health check endpoint for a service unavailable response (503).
    """
    def mock_health_check():
        return False

    monkeypatch.setattr('api.dummy_aadhaar_api.some_module.health_check', mock_health_check)
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 503
    assert response.get_json() == {'status': 'service_unavailable'}





def test_health_check_success(client):
    """
    Test the health check endpoint for a successful response (200).
    """
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}





def test_perform_ekyc_missing_field(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400






def test_perform_ekyc_success(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 200






def test_test_new_endpoint_success(client):
    response = client.get('/api/v1/aadhaar/test-new-endpoint')
    assert response.status_code == 200






def test_verify_aadhaar_invalid_aadhaar(client):
    """
    Test Aadhaar verification with invalid aadhaar_number.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'aadhaar_number': 'invalidaadhaarnumber',
        'captcha': 'abc123'
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()



def test_verify_aadhaar_invalid_captcha(client):
    """
    Test Aadhaar verification with invalid captcha.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'aadhaar_number': '123456789012',
        'captcha': 'wrongcaptcha'
    })
    assert response.status_code == 401
    assert 'error' in response.get_json()



def test_verify_aadhaar_missing_aadhaar(client):
    """
    Test Aadhaar verification with missing aadhaar_number.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'captcha': 'abc123'
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()



def test_verify_aadhaar_missing_captcha(client):
    """
    Test Aadhaar verification with missing captcha.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'aadhaar_number': '123456789012'
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()



def test_verify_aadhaar_success(client):
    """
    Test successful Aadhaar verification with valid payload.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'aadhaar_number': '123456789012',
        'captcha': 'abc123'
    })
    assert response.status_code == 200
    assert 'message' in response.get_json()



def test_verify_otp_missing_field(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={})
    assert response.status_code == 400






def test_verify_otp_success(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890', 'otp': '123456'})
    assert response.status_code == 200





