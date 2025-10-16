"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 AI-GENERATED API TEST SUITE                                  ║
║                 Powered by CodeLlama 70B                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 TEST GENERATION SUMMARY

🤖 AI Model:           CodeLlama 70B
📅 Generated:          2025-10-16 17:14:31
📂 Version:            v14
🔖 Spec Hash:          ee7e1792fce93137

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

def test_demographics_consent_denied():
    """
    Test demographic details retrieval with consent denied.
    """
    payload = {"aadhaar_number": "123456789012", "consent": False}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 403
    assert "error" in response.json()

def test_demographics_missing_field():
    """
    Test demographic details retrieval with missing field.
    """
    payload = {"aadhaar_number": "", "consent": True}
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_demographics_success(demographics_payload):
    """
    Test successful retrieval of demographic details.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=demographics_payload)
    assert response.status_code == 200
    assert "name" in response.json()
    assert "age" in response.json()


def test_verify_aadhaar_missing_field():
    """
    Test Aadhaar verification with missing field.
    """
    payload = {"aadhaar_number": ""}
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_verify_aadhaar_success(verify_aadhaar_payload):
    """
    Test successful Aadhaar verification.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=verify_aadhaar_payload)
    assert response.status_code == 200
    assert "message" in response.json()


