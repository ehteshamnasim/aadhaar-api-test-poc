import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"

@pytest.fixture
def session():
    return requests.Session()

def test_aadhaar_verify_success(session):
    """
    Test successful Aadhaar verification.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_aadhaar_verify_failure(session):
    """
    Test failure in Aadhaar verification with invalid payload.
    """
    payload = {"aadhaar_number": "invalid"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
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

def test_aadhaar_demographics_failure_missing_consent(session):
    """
    Test failure in retrieving Aadhaar demographics with missing consent.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_aadhaar_demographics_failure_forbidden(session):
    """
    Test forbidden access in retrieving Aadhaar demographics.
    """
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)

def test_aadhaar_otp_generate_success(session):
    """
    Test successful generation of Aadhaar OTP.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_aadhaar_otp_generate_failure(session):
    """
    Test failure in generating Aadhaar OTP with invalid payload.
    """
    payload = {"aadhaar_number": "invalid"}
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_aadhaar_otp_generate_rate_limited(session):
    """
    Test rate limiting in generating Aadhaar OTP.
    """
    payload = {"aadhaar_number": "123456789012"}
    for _ in range(10):  # Assuming the rate limit is 1 request per second
        response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload)
    assert response.status_code == 429
    assert isinstance(response.json(), dict)