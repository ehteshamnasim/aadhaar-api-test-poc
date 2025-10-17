"""AI-Generated Tests v24 - 2025-10-18 00:35:19"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()


def test_generate_otp_missing_field(client):
    """
    Test OTP generation with missing required field.
    """
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_generate_otp_success(client):
    """
    Test successful OTP generation with valid payload.
    """
    response = client.post('/api/v1/aadhaar/otp/generate', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
    assert 'transaction_id' in response.get_json()


def test_get_demographics_consent_denied(client):
    """
    Test retrieval of demographic details with consent denied.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': False})
    assert response.status_code == 403
    assert 'error' in response.get_json()


def test_get_demographics_missing_field(client):
    """
    Test retrieval of demographic details with missing required field.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_get_demographics_success(client):
    """
    Test successful retrieval of demographic details with valid payload.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 200
    assert 'demographics' in response.get_json()


def test_perform_ekyc_consent_denied(client):
    """
    Test eKYC with consent denied.
    """
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': False})
    assert response.status_code == 403
    assert 'error' in response.get_json()

def test_perform_ekyc_missing_field(client):
    """
    Test eKYC with missing required field.
    """
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890'})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_perform_ekyc_success(client):
    """
    Test successful eKYC with valid payload.
    """
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 200
    assert 'ekyc_details' in response.get_json()


def test_verify_aadhaar_missing_field(client):
    """
    Test Aadhaar verification with missing required field.
    """
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_verify_aadhaar_success(client):
    """
    Test successful Aadhaar verification with valid payload.
    """
    response = client.post('/api/v1/aadhaar/verify', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
    assert 'message' in response.get_json()


def test_verify_otp_missing_field(client):
    """
    Test OTP verification with missing required field.
    """
    response = client.post('/api/v1/aadhaar/otp/verify', json={})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_verify_otp_success(client):
    """
    Test successful OTP verification with valid payload.
    """
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890', 'otp': '123456'})
    assert response.status_code == 200
    assert 'message' in response.get_json()

