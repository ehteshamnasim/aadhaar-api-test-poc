"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 AI-GENERATED API TEST SUITE                                  ║
║                 Powered by CodeLlama 70B                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 TEST GENERATION SUMMARY

🤖 AI Model:           CodeLlama 70B
📅 Generated:          2025-10-16 18:51:56
📂 Version:            v15
🔖 Spec Hash:          bb196a9272ed4cbf

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

def test_get_demographics_invalid_consent(headers):
    """
    Test getting demographic details with an invalid consent value.
    Expected response status code: 403
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 403

def test_get_demographics_missing_aadhaar(headers):
    """
    Test getting demographic details with an invalid payload (missing aadhaar_number).
    Expected response status code: 400
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {"consent": True}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 400


def test_get_demographics_missing_consent(headers):
    """
    Test getting demographic details with an invalid payload (missing consent).
    Expected response status code: 400
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {"aadhaar_number": "123456789012"}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 400


def test_get_demographics_success(headers):
    """
    Test getting demographic details with a valid payload.
    Expected response status code: 200
    """
    url = f"{BASE_URL}/aadhaar/demographics"
    payload = {"aadhaar_number": "123456789012", "consent": True}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200


def test_verify_aadhaar_missing_field(headers):
    """
    Test verifying aadhaar number with an invalid payload (missing aadhaar_number).
    Expected response status code: 400
    """
    url = f"{BASE_URL}/aadhaar/verify"
    payload = {}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 400


def test_verify_aadhaar_success(headers):
    """
    Test verifying aadhaar number with a valid payload.
    Expected response status code: 200
    """
    url = f"{BASE_URL}/aadhaar/verify"
    payload = {"aadhaar_number": "123456789012"}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200


