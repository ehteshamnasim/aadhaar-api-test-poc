import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"

@pytest.fixture
def session():
    return requests.Session()

def test_aadhaar_verify_success(session):
    """
    Test successful Aadhaar verification with a valid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/verify", json={"aadhaar_number": "123456789012"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_aadhaar_verify_invalid_payload(session):
    """
    Test Aadhaar verification with an invalid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/verify", json={"aadhaar_number": "invalid"})
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_aadhaar_demographics_success(session):
    """
    Test successful retrieval of Aadhaar demographics with a valid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json={"aadhaar_number": "123456789012", "consent": True})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_aadhaar_demographics_missing_consent(session):
    """
    Test retrieval of Aadhaar demographics with a missing consent field.
    """
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json={"aadhaar_number": "123456789012"})
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_aadhaar_demographics_invalid_consent(session):
    """
    Test retrieval of Aadhaar demographics with an invalid consent value.
    """
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json={"aadhaar_number": "123456789012", "consent": "invalid"})
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_aadhaar_demographics_unauthorized(session):
    """
    Test retrieval of Aadhaar demographics with unauthorized access.
    """
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json={"aadhaar_number": "123456789012", "consent": False})
    assert response.status_code == 403
    assert isinstance(response.json(), dict)

def test_aadhaar_otp_generate_success(session):
    """
    Test successful generation of Aadhaar OTP with a valid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json={"aadhaar_number": "123456789012"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_aadhaar_otp_generate_invalid_payload(session):
    """
    Test generation of Aadhaar OTP with an invalid payload.
    """
    response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json={"aadhaar_number": "invalid"})
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_aadhaar_otp_generate_rate_limited(session):
    """
    Test generation of Aadhaar OTP with rate limiting.
    """
    # Simulate multiple requests to trigger rate limiting
    for _ in range(10):
        response = session.post(f"{BASE_URL}/aadhaar/otp/generate", json={"aadhaar_number": "123456789012"})
    assert response.status_code == 429
    assert isinstance(response.json(), dict)