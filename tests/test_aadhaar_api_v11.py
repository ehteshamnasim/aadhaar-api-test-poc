"""
AI-Generated API Tests - v11
Generated: 2025-10-16 23:14:24
Endpoints: 5 | Tests: 14
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



def test_generate_otp_invalid_payload(session):
    """
    Test generating OTP for Aadhaar with an invalid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json={})
    assert response.status_code == 400
    assert "error" in response.json()


def test_generate_otp_success(session):
    """
    Test generating OTP for Aadhaar with a valid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json={"aadhaar_number": "123456789012"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_demographics_invalid_consent(session):
    """
    Test getting demographic details with an invalid consent field.
    """
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json={"aadhaar_number": "123456789012", "consent": "invalid"})
    assert response.status_code == 400
    assert "error" in response.json()


def test_get_demographics_missing_consent(session):
    """
    Test getting demographic details with a missing consent field.
    """
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json={"aadhaar_number": "123456789012"})
    assert response.status_code == 400
    assert "error" in response.json()


def test_get_demographics_permission_denied(session):
    """
    Test getting demographic details with permission denied.
    """
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json={"aadhaar_number": "123456789012", "consent": False})
    assert response.status_code == 403
    assert "error" in response.json()


def test_get_demographics_success(session):
    """
    Test getting demographic details with a valid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json={"aadhaar_number": "123456789012", "consent": True})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_perform_ekyc_invalid_consent(session):
    """
    Test performing eKYC with an invalid consent field.
    """
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json={"aadhaar_number": "123456789012", "transaction_id": "1234567890", "consent": "invalid"})
    assert response.status_code == 400
    assert "error" in response.json()


def test_perform_ekyc_missing_consent(session):
    """
    Test performing eKYC with a missing consent field.
    """
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json={"aadhaar_number": "123456789012", "transaction_id": "1234567890"})
    assert response.status_code == 400
    assert "error" in response.json()


def test_perform_ekyc_permission_denied(session):
    """
    Test performing eKYC with permission denied.
    """
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json={"aadhaar_number": "123456789012", "transaction_id": "1234567890", "consent": False})
    assert response.status_code == 403
    assert "error" in response.json()

def test_perform_ekyc_success(session):
    """
    Test performing eKYC with a valid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/ekyc", json={"aadhaar_number": "123456789012", "transaction_id": "1234567890", "consent": True})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_invalid_payload(session):
    """
    Test verifying Aadhaar number with an invalid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/verify", json={})
    assert response.status_code == 400
    assert "error" in response.json()


def test_verify_aadhaar_success(session):
    """
    Test verifying Aadhaar number with a valid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/verify", json={"aadhaar_number": "123456789012"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_otp_invalid_payload(session):
    """
    Test verifying OTP with an invalid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json={})
    assert response.status_code == 400
    assert "error" in response.json()


def test_verify_otp_success(session):
    """
    Test verifying OTP with a valid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/otp/verify", json={"transaction_id": "1234567890", "otp": "123456"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

