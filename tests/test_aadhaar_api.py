import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"

@pytest.fixture
def headers():
    return {"Content-Type": "application/json"}

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

def test_verify_aadhaar_missing_field(headers):
    """
    Test verification of Aadhaar number with missing field.
    """
    payload = {}
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_success(headers):
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

def test_demographics_missing_field(headers):
    """
    Test retrieval of demographic details with missing field.
    """
    payload = {
        "consent": True
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_invalid_consent(headers):
    """
    Test retrieval of demographic details with invalid consent value.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": "invalid"
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_unauthorized(headers):
    """
    Test retrieval of demographic details without proper authorization.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": True
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)