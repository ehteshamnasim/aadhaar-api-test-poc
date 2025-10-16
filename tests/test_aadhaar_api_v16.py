"""AI-Generated Tests v16 - 2025-10-17 00:05:28"""
import pytest
import requests

BASE_URL = "http://localhost:5001/api/v1"

@pytest.fixture(scope="session")
def session():
    with requests.Session() as s:
        s.headers.update({'Content-Type': 'application/json'})
        yield s

@pytest.fixture(scope="session", autouse=True)
def check_api():
    try:
        r = requests.get(BASE_URL.replace('/api/v1', '/health'), timeout=3)
        assert r.status_code == 200
    except:
        pytest.fail("API unavailable")


def test_generate_otp_missing_field(client):
    """
    Test generation of OTP with missing field.
    """
    response = client.post('/aadhaar/otp/generate', json={})
    assert response.status_code == 400
    assert 'error' in response.json


def test_generate_otp_success(client):
    """
    Test successful generation of OTP.
    """
    response = client.post('/aadhaar/otp/generate', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
    assert 'transaction_id' in response.json


def test_get_demographics_invalid_consent(client):
    """
    Test retrieval of demographic details with invalid consent.
    """
    response = client.post('/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': 'invalid'})
    assert response.status_code == 400
    assert 'error' in response.json


def test_get_demographics_missing_field(client):
    """
    Test retrieval of demographic details with missing field.
    """
    response = client.post('/aadhaar/demographics', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400
    assert 'error' in response.json


def test_get_demographics_success(client):
    """
    Test successful retrieval of demographic details.
    """
    response = client.post('/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 200
    assert 'demographics' in response.json


def test_perform_ekyc_invalid_consent(client):
    """
    Test eKYC with invalid consent.
    """
    response = client.post('/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': 'invalid'})
    assert response.status_code == 400
    assert 'error' in response.json

def test_perform_ekyc_missing_field(client):
    """
    Test eKYC with missing field.
    """
    response = client.post('/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890'})
    assert response.status_code == 400
    assert 'error' in response.json


def test_perform_ekyc_success(client):
    """
    Test successful eKYC.
    """
    response = client.post('/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 200
    assert 'ekyc_details' in response.json


def test_verify_aadhaar_missing_field(client):
    """
    Test verification of Aadhaar number with missing field.
    """
    response = client.post('/aadhaar/verify', json={})
    assert response.status_code == 400
    assert 'error' in response.json


def test_verify_aadhaar_success(client):
    """
    Test successful verification of Aadhaar number.
    """
    response = client.post('/aadhaar/verify', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
    assert 'message' in response.json


def test_verify_otp_missing_field(client):
    """
    Test verification of OTP with missing field.
    """
    response = client.post('/aadhaar/otp/verify', json={'transaction_id': '1234567890'})
    assert response.status_code == 400
    assert 'error' in response.json


def test_verify_otp_success(client):
    """
    Test successful verification of OTP.
    """
    response = client.post('/aadhaar/otp/verify', json={'transaction_id': '1234567890', 'otp': '123456'})
    assert response.status_code == 200
    assert 'message' in response.json

