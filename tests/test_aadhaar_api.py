import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"

@pytest.fixture
def headers():
    return {"Content-Type": "application/json"}

# Tests for /aadhaar/verify endpoint

def test_verify_aadhaar_success(headers):
    """
    Test successful verification of Aadhaar number.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_verify_aadhaar_invalid_payload(headers):
    """
    Test verification of Aadhaar number with invalid payload.
    """
    payload = {"aadhaar_number": "invalid"}
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

# Tests for /aadhaar/demographics endpoint

def test_demographics_success(headers):
    """
    Test successful retrieval of demographic details.
    """
    payload = {"aadhaar_number": "123456789012", "consent": True}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_demographics_missing_consent(headers):
    """
    Test retrieval of demographic details with missing consent.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_invalid_consent(headers):
    """
    Test retrieval of demographic details with invalid consent.
    """
    payload = {"aadhaar_number": "123456789012", "consent": "invalid"}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_forbidden(headers):
    """
    Test retrieval of demographic details with forbidden access.
    """
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)

# Tests for /aadhaar/otp/generate endpoint

def test_generate_otp_success(headers):
    """
    Test successful generation of OTP.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = requests.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_generate_otp_invalid_payload(headers):
    """
    Test generation of OTP with invalid payload.
    """
    payload = {"aadhaar_number": "invalid"}
    response = requests.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_generate_otp_rate_limited(headers):
    """
    Test generation of OTP with rate limiting.
    """
    payload = {"aadhaar_number": "123456789012"}
    # Simulate multiple requests to trigger rate limit
    for _ in range(10):  # Assuming rate limit is 1 request per second
        response = requests.post(f"{BASE_URL}/aadhaar/otp/generate", json=payload, headers=headers)
    assert response.status_code == 429
    assert isinstance(response.json(), dict)