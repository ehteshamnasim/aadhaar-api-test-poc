import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"

@pytest.fixture(scope="module")
def session():
    return requests.Session()

def test_verify_aadhaar_success(session):
    """
    Test successful verification of Aadhaar number.
    """
    payload = {
        "aadhaar_number": "123456789012"
    }
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_verify_aadhaar_missing_field(session):
    """
    Test verification of Aadhaar number with missing field.
    """
    payload = {}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_success(session):
    """
    Test successful retrieval of demographic details.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": True
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_demographics_missing_field(session):
    """
    Test retrieval of demographic details with missing field.
    """
    payload = {
        "consent": True
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_demographics_forbidden(session):
    """
    Test retrieval of demographic details with forbidden access.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": False
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)