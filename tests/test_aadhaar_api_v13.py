"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 AI-GENERATED API TEST SUITE                                  ║
║                 Powered by CodeLlama 70B                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 TEST GENERATION SUMMARY

🤖 AI Model:           CodeLlama 70B
📅 Generated:          2025-10-16 17:06:58
📂 Version:            v13
🔖 Spec Hash:          481de6514ad87c2e

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
    Test retrieval of demographic details with invalid consent value.
    """
    payload = {"aadhaar_number": "123456789012", "consent": "invalid"}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_get_demographics_missing_field(headers):
    """
    Test retrieval of demographic details with missing field.
    """
    payload = {"aadhaar_number": "123456789012"}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)


def test_get_demographics_success(headers):
    """
    Test successful retrieval of demographic details.
    """
    payload = {"aadhaar_number": "123456789012", "consent": True}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_demographics_unauthorized(headers):
    """
    Test retrieval of demographic details without proper authorization.
    """
    payload = {"aadhaar_number": "123456789012", "consent": True}
    headers.pop("Authorization")  # Assuming Authorization header is required for 403
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload, headers=headers)
    assert response.status_code == 403
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
    payload = {"aadhaar_number": "123456789012"}
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


