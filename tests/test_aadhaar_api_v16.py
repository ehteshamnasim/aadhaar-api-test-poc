"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 AI-GENERATED API TEST SUITE                                  ║
║                 Powered by CodeLlama 70B                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 TEST GENERATION SUMMARY

🤖 AI Model:           CodeLlama 70B
📅 Generated:          2025-10-16 20:25:01
📂 Version:            v16
🔖 Spec Hash:          1b0d4efd05bf7701

📊 API SPECIFICATION

📄 Spec File:          specs/aadhaar-api.yaml
🌐 Total Endpoints:    2
🔗 Base URL:           http://localhost:5001/api/v1

Endpoints:
  1. POST   /aadhaar/verify
  2. POST   /aadhaar/demographics

🧪 TEST SUITE

✓ Total Tests:         6
✓ Framework:           pytest
✓ Coverage Target:     ≥85%

"""


import pytest
import requests

def test_aadhaar_demographics_invalid_consent(session):
    """
    Test retrieval of demographic details with invalid consent value.
    """
    payload = {
        'aadhaar_number': '123456789012',
        'consent': "invalid"
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert 'error' in response.json()


def test_aadhaar_demographics_missing_field(session):
    """
    Test retrieval of demographic details with missing required field.
    """
    payload = {
        'consent': True
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert 'error' in response.json()


def test_aadhaar_demographics_success(session):
    """
    Test successful retrieval of demographic details with valid payload.
    """
    payload = {
        'aadhaar_number': '123456789012',
        'consent': True
    }
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_demographics_unauthorized(session):
    """
    Test retrieval of demographic details without proper authorization.
    """
    payload = {
        'aadhaar_number': '123456789012',
        'consent': True
    }
    # Simulate unauthorized access by not sending necessary headers or tokens
    response = session.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert 'error' in response.json()

def test_aadhaar_verify_missing_field(session):
    """
    Test verification with missing required field.
    """
    payload = {}
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert 'error' in response.json()


def test_aadhaar_verify_success(session):
    """
    Test successful verification of a valid Aadhaar number.
    """
    payload = {
        'aadhaar_number': '123456789012'
    }
    response = session.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


