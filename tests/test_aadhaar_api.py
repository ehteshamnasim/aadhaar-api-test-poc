import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"

@pytest.fixture
def headers():
    return {"Content-Type": "application/json"}

def test_verify_aadhaar_success(headers):
    """
    Test verifying Aadhaar number with a valid payload.
    Expected response status code: 200
    """
    payload = {
        "aadhaar_number": "123456789012"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_verify_aadhaar_missing_field(headers):
    """
    Test verifying Aadhaar number with a missing field.
    Expected response status code: 400
    """
    payload = {}
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_success(headers):
    """
    Test getting demographic details with a valid payload.
    Expected response status code: 200
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": True
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_demographics_missing_field(headers):
    """
    Test getting demographic details with a missing field.
    Expected response status code: 400
    """
    payload = {
        "aadhaar_number": "123456789012"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_invalid_consent(headers):
    """
    Test getting demographic details with an invalid consent value.
    Expected response status code: 403
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": "invalid"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)