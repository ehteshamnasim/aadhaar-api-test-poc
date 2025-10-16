"""
AI-Generated API Tests - v7
Generated: 2025-10-16 21:29:20
Endpoints: 2 | Tests: 6
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



def test_demographics_forbidden(headers):
    """
    Test retrieval of demographic details with forbidden access.
    """
    payload = {
        "aadhaar_number": "123456789012",
        "consent": False
    }
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 403
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


def test_verify_aadhaar_missing_field(headers):
    """
    Test verification of Aadhaar number with missing field.
    """
    payload = {}
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


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

