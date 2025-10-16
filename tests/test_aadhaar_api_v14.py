"""
AI-Generated API Tests - v14
Generated: 2025-10-16 23:39:55
Endpoints: 5 | Tests: 12
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
        print("\n✅ API is accessible")
    except Exception as e:
        pytest.fail(f"❌ API not running: {e}")



def test_ekyc_invalid_consent(headers):
    """
    Test eKYC with invalid consent.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "transaction_id": "123456",
        "consent": "invalid"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/ekyc", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_ekyc_missing_consent(headers):
    """
    Test eKYC with missing consent.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "transaction_id": "123456"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/ekyc", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_ekyc_success(headers):
    """
    Test successful eKYC.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "transaction_id": "123456",
        "consent": True
    }
    response = requests.post(f"{BASE_URL}/aadhaar/ekyc", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_generate_otp_invalid_payload(headers):
    """
    Test generation of OTP with invalid payload.
    """
    payload = {}
    response = requests.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_generate_otp_success(headers):
    """
    Test successful generation of OTP.
    """
    payload = {
        "aadhaar_number": "123456789012"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_demographics_invalid_consent(headers):
    """
    Test retrieval of demographic details with invalid consent.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": "invalid"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_get_demographics_missing_consent(headers):
    """
    Test retrieval of demographic details with missing consent.
    """
    payload = {
        "aadhaar_number": "123456789012"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_get_demographics_success(headers):
    """
    Test successful retrieval of demographic details.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": True
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_invalid_payload(headers):
    """
    Test verification of Aadhaar number with invalid payload.
    """
    payload = {}
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_success(headers):
    """
    Test successful verification of Aadhaar number.
    """
    payload = {
        "aadhaar_number": "123456789012"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_otp_invalid_payload(headers):
    """
    Test verification of OTP with invalid payload.
    """
    payload = {}
    response = requests.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_verify_otp_success(headers):
    """
    Test successful verification of OTP.
    """
    payload = {
        "transaction_id": "123456",
        "otp": "123456"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/otp/verify", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

