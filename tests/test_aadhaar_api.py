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

# --- New tests from spec change (2025-10-16 15:55:39) ---

def test_verify_aadhaar_invalid_payload(invalid_verify_aadhaar_payload):
    """
    Test verification of Aadhaar number with invalid payload.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=invalid_verify_aadhaar_payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_demographics_invalid_payload(invalid_demographics_payload):
    """
    Test retrieval of demographic details with invalid payload.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=invalid_demographics_payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_demographics_missing_consent():
    """
    Test retrieval of demographic details without consent field.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_demographics_forbidden_access():
    """
    Test retrieval of demographic details with forbidden access.
    """
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)


# --- New tests (2025-10-16 16:08:23) ---

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
    # Simulate unauthorized access by not providing necessary headers or tokens
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)
