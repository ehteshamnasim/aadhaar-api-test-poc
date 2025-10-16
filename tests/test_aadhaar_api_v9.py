"""
AI-Generated API Tests - v9
Generated: 2025-10-16 21:38:22
Endpoints: 5 | Tests: 12
"""

import pytest
import requests


BASE_URL = "http://localhost:5001/api/v1"


@pytest.fixture(scope="session")
def session():
    """Provides requests Session"""
    with requests.Session() as s:
        s.headers.update({'Content-Type': 'application/json'})
        yield s


@pytest.fixture(scope="session", autouse=True)
def check_api():
    """Verify API is running"""
    try:
        r = requests.get(BASE_URL.replace('/api/v1', '/health'), timeout=3)
        assert r.status_code == 200
        print("\n✅ API accessible")
    except Exception as e:
        pytest.fail(f"❌ API not running: {e}")



def test_aadhaar_demographics_invalid_consent(session):
    """
    Test Aadhaar demographics with invalid consent value.
    """
    payload = {"aadhaar_number": "123456789012", "consent": "invalid"}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_demographics_missing_field(session):
    """
    Test Aadhaar demographics with missing field.
    """
    payload = {"consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_demographics_success(session):
    """
    Test successful retrieval of Aadhaar demographics.
    """
    payload = {"aadhaar_number": "123456789012", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_ekyc_invalid_consent(session):
    """
    Test eKYC with invalid consent value.
    """
    payload = {"aadhaar_number": "123456789012", "transaction_id": "1234567890", "consent": "invalid"}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_aadhaar_ekyc_missing_field(session):
    """
    Test eKYC with missing field.
    """
    payload = {"transaction_id": "1234567890", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_ekyc_success(session):
    """
    Test successful eKYC.
    """
    payload = {"aadhaar_number": "123456789012", "transaction_id": "1234567890", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_otp_generate_missing_field(session):
    """
    Test OTP generation with missing field.
    """
    payload = {}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_otp_generate_success(session):
    """
    Test successful OTP generation for Aadhaar.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_otp_verify_missing_field(session):
    """
    Test OTP verification with missing field.
    """
    payload = {"transaction_id": "1234567890"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_otp_verify_success(session):
    """
    Test successful OTP verification.
    """
    payload = {"transaction_id": "1234567890", "otp": "123456"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_verify_missing_field(session):
    """
    Test Aadhaar verification with missing field.
    """
    payload = {}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_verify_success(session):
    """
    Test successful Aadhaar verification.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

