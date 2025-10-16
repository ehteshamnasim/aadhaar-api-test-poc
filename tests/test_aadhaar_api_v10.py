"""
AI-Generated API Tests - v10
Generated: 2025-10-16 23:07:22
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



def test_ekyc_forbidden(session):
    """
    Test eKYC with forbidden access.
    """
    payload = {"aadhaar_number": "123456789012", "transaction_id": "123456", "consent": False}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)

def test_ekyc_missing_consent(session):
    """
    Test eKYC with missing consent.
    """
    payload = {"aadhaar_number": "123456789012", "transaction_id": "123456"}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_ekyc_success(session):
    """
    Test successful eKYC.
    """
    payload = {"aadhaar_number": "123456789012", "transaction_id": "123456", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_generate_otp_invalid_payload(session):
    """
    Test OTP generation with invalid payload.
    """
    payload = {"aadhaar_number": "invalid"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_generate_otp_success(session):
    """
    Test successful OTP generation.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_demographics_forbidden(session):
    """
    Test retrieval of demographic details with forbidden access.
    """
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)


def test_get_demographics_missing_consent(session):
    """
    Test retrieval of demographic details with missing consent.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_get_demographics_success(session):
    """
    Test successful retrieval of demographic details.
    """
    payload = {"aadhaar_number": "123456789012", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_invalid_payload(session):
    """
    Test Aadhaar verification with invalid payload.
    """
    payload = {"aadhaar_number": "invalid"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_success(session):
    """
    Test successful Aadhaar verification.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_otp_invalid_payload(session):
    """
    Test OTP verification with invalid payload.
    """
    payload = {"transaction_id": "123456"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_verify_otp_success(session):
    """
    Test successful OTP verification.
    """
    payload = {"transaction_id": "123456", "otp": "123456"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

