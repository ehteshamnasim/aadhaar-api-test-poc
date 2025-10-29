"""AI-Generated Tests v60 - 2025-10-29 20:07:44"""
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




def test_get_masked_aadhaar_missing_fields(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 400




def test_get_masked_aadhaar_success(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 200




def test_health_check_service_unavailable(client):
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 503



def test_health_check_success(client):
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 200




def test_perform_ekyc_missing_fields(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400




def test_perform_ekyc_no_consent(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': False})
    assert response.status_code == 403




def test_perform_ekyc_success(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 200




def test_test_new_endpoint_success(client):
    response = client.get('/api/v1/aadhaar/test-new-endpoint')
    assert response.status_code == 200




def test_verify_aadhaar_invalid_captcha(client):
    """
    Test verification of Aadhaar number with invalid captcha.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'aadhaar_number': '123456789012',
        'captcha': 'invalid_captcha'
    })
    assert response.status_code == 401
    assert 'error' in response.get_json()



def test_verify_aadhaar_missing_aadhaar(client):
    """
    Test verification of Aadhaar number with missing aadhaar_number.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'captcha': 'valid_captcha'
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()



def test_verify_aadhaar_missing_captcha(client):
    """
    Test verification of Aadhaar number with missing captcha.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'aadhaar_number': '123456789012'
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()



def test_verify_aadhaar_rate_limit_exceeded(client):
    """
    Test verification of Aadhaar number when rate limit is exceeded.
    """
    # Simulate rate limit by sending multiple requests
    for _ in range(10):  # Assuming the rate limit is 9 requests per minute
        response = client.post('/api/v1/aadhaar/verify', json={
            'aadhaar_number': '123456789012',
            'captcha': 'valid_captcha'
        })
    assert response.status_code == 429
    assert 'error' in response.get_json()



def test_verify_aadhaar_success(client):
    """
    Test successful verification of Aadhaar number with valid payload.
    """
    response = client.post('/api/v1/aadhaar/verify', json={
        'aadhaar_number': '123456789012',
        'captcha': 'valid_captcha'
    })
    assert response.status_code == 200
    assert 'message' in response.get_json()



def test_verify_otp_missing_fields(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890'})
    assert response.status_code == 400




def test_verify_otp_success(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890', 'otp': '123456'})
    assert response.status_code == 200



