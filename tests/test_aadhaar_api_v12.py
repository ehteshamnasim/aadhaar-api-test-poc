"""
AI-Generated API Tests - v12
Generated: 2025-10-16 23:22:42
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



def test_aadhaar_demographics_failure(session):
    """
    Test failure in retrieving demographic details with invalid payload.
    """
    payload = {"aadhaar_number": "invalid", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_demographics_success(session):
    """
    Test successful retrieval of demographic details.
    """
    payload = {"aadhaar_number": "123456789012", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_demographics_unauthorized(session):
    """
    Test unauthorized access to demographic details.
    """
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)


def test_aadhaar_ekyc_failure(session):
    """
    Test failure in eKYC with invalid payload.
    """
    payload = {"aadhaar_number": "invalid", "transaction_id": "1234567890", "consent": True}
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


def test_aadhaar_ekyc_unauthorized(session):
    """
    Test unauthorized access to eKYC.
    """
    payload = {"aadhaar_number": "123456789012", "transaction_id": "1234567890", "consent": False}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)

def test_aadhaar_otp_generate_failure(session):
    """
    Test failure in generating OTP with invalid payload.
    """
    payload = {"aadhaar_number": "invalid"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_otp_generate_success(session):
    """
    Test successful generation of OTP for Aadhaar.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_otp_verify_failure(session):
    """
    Test failure in verifying OTP with invalid payload.
    """
    payload = {"transaction_id": "invalid", "otp": "123456"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_otp_verify_success(session):
    """
    Test successful verification of OTP.
    """
    payload = {"transaction_id": "1234567890", "otp": "123456"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_verify_failure(session):
    """
    Test failure in verifying Aadhaar number with invalid payload.
    """
    payload = {"aadhaar_number": "invalid"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_verify_success(session):
    """
    Test successful verification of Aadhaar number.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

