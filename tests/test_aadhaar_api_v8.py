"""
AI-Generated API Tests - v8
Generated: 2025-10-16 21:30:30
Endpoints: 2 | Tests: 7
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



def test_demographics_forbidden(session):
    """
    Test demographic details retrieval with forbidden access.
    """
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)


def test_demographics_invalid_aadhaar(session):
    """
    Test demographic details retrieval with invalid Aadhaar number.
    """
    payload = {"aadhaar_number": "invalid123", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_demographics_missing_field(session):
    """
    Test demographic details retrieval with missing field.
    """
    payload = {"consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_demographics_success(session):
    """
    Test successful retrieval of demographic details.
    """
    payload = {"aadhaar_number": "123456789012", "consent": True}
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_invalid_aadhaar(session):
    """
    Test Aadhaar verification with invalid Aadhaar number.
    """
    payload = {"aadhaar_number": "invalid123"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

def test_verify_aadhaar_missing_field(session):
    """
    Test Aadhaar verification with missing field.
    """
    payload = {}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_success(session):
    """
    Test successful Aadhaar verification.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

