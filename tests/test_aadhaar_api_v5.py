"""AI-Generated Tests v5 - 2025-10-17 01:10:58"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()


def test_generate_otp_missing_field(client):
    """
    Test missing required field for OTP generation.
    """
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400


def test_generate_otp_success(client):
    """
    Test successful generation of OTP.
    """
    response = client.post('/api/v1/aadhaar/otp/generate', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200


def test_get_demographics_consent_denied(client):
    """
    Test retrieval of demographic details with consent denied.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': False})
    assert response.status_code == 403


def test_get_demographics_missing_field(client):
    """
    Test missing required field for demographic retrieval.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400


def test_get_demographics_success(client):
    """
    Test successful retrieval of demographic details.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 200


def test_perform_ekyc_consent_denied(client):
    """
    Test eKYC process with consent denied.
    """
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': False})
    assert response.status_code == 403

def test_perform_ekyc_missing_field(client):
    """
    Test missing required field for eKYC process.
    """
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400


def test_perform_ekyc_success(client):
    """
    Test successful eKYC process.
    """
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 200


def test_verify_aadhaar_missing_field(client):
    """
    Test missing required field for Aadhaar verification.
    """
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400


def test_verify_aadhaar_success(client):
    """
    Test successful verification of Aadhaar number.
    """
    response = client.post('/api/v1/aadhaar/verify', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200


def test_verify_otp_missing_field(client):
    """
    Test missing required field for OTP verification.
    """
    response = client.post('/api/v1/aadhaar/otp/verify', json={})
    assert response.status_code == 400


def test_verify_otp_success(client):
    """
    Test successful verification of OTP.
    """
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890', 'otp': '123456'})
    assert response.status_code == 200

