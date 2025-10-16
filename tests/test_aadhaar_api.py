import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"

@pytest.fixture
def headers():
    return {"Content-Type": "application/json"}

def test_verify_aadhaar_success(headers):
    """
    Test the /aadhaar/verify endpoint with a valid payload.
    """
    response = requests.post(
        f"{BASE_URL}/aadhaar/verify",
        json={"aadhaar_number": "123456789012"},
        headers=headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_verify_aadhaar_missing_field(headers):
    """
    Test the /aadhaar/verify endpoint with a missing field.
    """
    response = requests.post(
        f"{BASE_URL}/aadhaar/verify",
        json={},
        headers=headers
    )
    assert response.status_code == 400

def test_demographics_success(headers):
    """
    Test the /aadhaar/demographics endpoint with a valid payload.
    """
    response = requests.post(
        f"{BASE_URL}/aadhaar/demographics",
        json={"aadhaar_number": "123456789012", "consent": True},
        headers=headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_demographics_missing_field(headers):
    """
    Test the /aadhaar/demographics endpoint with a missing field.
    """
    response = requests.post(
        f"{BASE_URL}/aadhaar/demographics",
        json={"aadhaar_number": "123456789012"},
        headers=headers
    )
    assert response.status_code == 400

def test_demographics_unauthorized(headers):
    """
    Test the /aadhaar/demographics endpoint with unauthorized access.
    """
    response = requests.post(
        f"{BASE_URL}/aadhaar/demographics",
        json={"aadhaar_number": "123456789012", "consent": False},
        headers=headers
    )
    assert response.status_code == 403

def test_generate_otp_success(headers):
    """
    Test the /aadhaar/otp/generate endpoint with a valid payload.
    """
    response = requests.post(
        f"{BASE_URL}/aadhaar/otp/generate",
        json={"aadhaar_number": "123456789012"},
        headers=headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_generate_otp_missing_field(headers):
    """
    Test the /aadhaar/otp/generate endpoint with a missing field.
    """
    response = requests.post(
        f"{BASE_URL}/aadhaar/otp/generate",
        json={},
        headers=headers
    )
    assert response.status_code == 400

def test_generate_otp_rate_limited(headers):
    """
    Test the /aadhaar/otp/generate endpoint with rate limiting.
    """
    # This test assumes that rate limiting is triggered after multiple requests
    for _ in range(10):  # Assuming rate limit is 1 request per second
        response = requests.post(
            f"{BASE_URL}/aadhaar/otp/generate",
            json={"aadhaar_number": "123456789012"},
            headers=headers
        )
    assert response.status_code == 429