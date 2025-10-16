"""
AI-Generated API Tests - v6
Generated: 2025-10-16 21:28:24
Endpoints: 2 | Tests: 5
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



def test_demographics_invalid_payload(session):
    """
    Test getting demographic details with an invalid payload.
    """
    payload = {
        'aadhaar_number': '',
        'consent': True
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_demographics_no_consent(session):
    """
    Test getting demographic details without consent.
    """
    payload = {
        'aadhaar_number': '123456789012',
        'consent': False
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)

def test_demographics_success(session):
    """
    Test getting demographic details with valid payload.
    """
    payload = {
        'aadhaar_number': '123456789012',
        'consent': True
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_invalid_payload(session):
    """
    Test verifying Aadhaar with an invalid payload.
    """
    payload = {
        'aadhaar_number': ''
    }
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_verify_aadhaar_success(session):
    """
    Test verifying a valid Aadhaar number.
    """
    payload = {
        'aadhaar_number': '123456789012'
    }
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

