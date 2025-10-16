"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 AI-GENERATED API TEST SUITE                                  ║
║                 Powered by CodeLlama 70B                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 TEST GENERATION SUMMARY

🤖 AI Model:           CodeLlama 70B
📅 Generated:          2025-10-16 20:18:31
📂 Version:            v15
🔖 Spec Hash:          3926403f29ff13aa

📊 API SPECIFICATION

📄 Spec File:          specs/aadhaar-api.yaml
🌐 Total Endpoints:    2
🔗 Base URL:           http://localhost:5001/api/v1

Endpoints:
  1. POST   /aadhaar/verify
  2. POST   /aadhaar/demographics

🧪 TEST SUITE

✓ Total Tests:         5
✓ Framework:           pytest
✓ Coverage Target:     ≥85%

"""


import pytest
import requests

def test_aadhaar_demographics_invalid_payload(session):
    """
    Test retrieval of demographic details with an invalid payload (missing field).
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(url, json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_demographics_success(session):
    """
    Test successful retrieval of demographic details with a valid payload.
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {"aadhaar_number": "123456789012", "consent": True}
    response = session.post(url, json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_aadhaar_demographics_unauthorized(session):
    """
    Test retrieval of demographic details with unauthorized access (consent=False).
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = session.post(url, json=payload)
    assert response.status_code == 403
    assert isinstance(response.json(), dict)

def test_aadhaar_verify_invalid_payload(session):
    """
    Test Aadhaar verification with an invalid payload (missing field).
    """
    url = f"{BASE_URL}/aadhaar/verify"
    payload = {}
    response = session.post(url, json=payload)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_aadhaar_verify_success(session):
    """
    Test successful Aadhaar verification with a valid payload.
    """
    url = f"{BASE_URL}/aadhaar/verify"
    payload = {"aadhaar_number": "123456789012"}
    response = session.post(url, json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


