import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"

@pytest.fixture
def valid_aadhaar_number():
    return "123456789012"

@pytest.fixture
def invalid_aadhaar_number():
    return "12345678901"  # Invalid Aadhaar number

def test_verify_aadhaar_success(valid_aadhaar_number):
    """
    Test successful verification of a valid Aadhaar number.
    """
    url = f"{BASE_URL}/aadhaar/verify"
    payload = {
        "aadhaar_number": valid_aadhaar_number
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200

def test_verify_aadhaar_invalid_payload():
    """
    Test verification with an invalid payload (missing required field).
    """
    url = f"{BASE_URL}/aadhaar/verify"
    payload = {}  # Missing 'aadhaar_number'
    response = requests.post(url, json=payload)
    assert response.status_code == 400

def test_verify_aadhaar_invalid_aadhaar(invalid_aadhaar_number):
    """
    Test verification with an invalid Aadhaar number.
    """
    url = f"{BASE_URL}/aadhaar/verify"
    payload = {
        "aadhaar_number": invalid_aadhaar_number
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 400

def test_demographics_success(valid_aadhaar_number):
    """
    Test successful retrieval of demographic details with valid Aadhaar number and consent.
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {
        "aadhaar_number": valid_aadhaar_number,
        "consent": True
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200

def test_demographics_invalid_payload():
    """
    Test retrieval of demographic details with an invalid payload (missing required field).
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {}  # Missing 'aadhaar_number' and 'consent'
    response = requests.post(url, json=payload)
    assert response.status_code == 400

def test_demographics_invalid_aadhaar(invalid_aadhaar_number):
    """
    Test retrieval of demographic details with an invalid Aadhaar number.
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {
        "aadhaar_number": invalid_aadhaar_number,
        "consent": True
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 400

def test_demographics_no_consent(valid_aadhaar_number):
    """
    Test retrieval of demographic details without consent.
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {
        "aadhaar_number": valid_aadhaar_number,
        "consent": False
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 403