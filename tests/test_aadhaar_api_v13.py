"""
AI-Generated API Tests - v13
Generated: 2025-10-16 23:31:24
"""

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
    except Exception as e:
        pytest.fail(f"❌ API not running: {e}")



def test_generate_otp_missing_field(session):
    """
    Test generation of OTP with missing field.
    """
    payload = {}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_generate_otp_success(session):
    """
    Test successful generation of OTP.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_demographics_missing_field(session):
    """
    Test retrieval of demographic details with missing field.
    """
    payload = {"consent": True}
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


def test_get_demographics_unauthorized(session):
    """
    Test retrieval of demographic details with unauthorized access.
    """
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)


def test_perform_ekyc_missing_field(session):
    """
    Test eKYC with missing field.
    """
    payload = {"transaction_id": "123456", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_perform_ekyc_success(session):
    """
    Test successful eKYC.
    """
    payload = {"aadhaar_number": "123456789012", "transaction_id": "123456", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_perform_ekyc_unauthorized(session):
    """
    Test eKYC with unauthorized access.
    """
    payload = {"aadhaar_number": "123456789012", "transaction_id": "123456", "consent": False}
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)

def test_verify_aadhaar_missing_field(session):
    """
    Test verification of Aadhaar number with missing field.
    """
    payload = {}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_success(session):
    """
    Test successful verification of Aadhaar number.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_otp_missing_field(session):
    """
    Test verification of OTP with missing field.
    """
    payload = {"transaction_id": "123456"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_verify_otp_success(session):
    """
    Test successful verification of OTP.
    """
    payload = {"transaction_id": "123456", "otp": "123456"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

