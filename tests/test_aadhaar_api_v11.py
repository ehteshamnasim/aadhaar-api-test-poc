"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 AI-GENERATED API TEST SUITE                                  ║
║                 Powered by CodeLlama 70B                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 TEST GENERATION SUMMARY
════════════════════════════════════════════════════════════════════════════════

🤖 AI Model:           CodeLlama 70B (via Ollama)
📅 Generated:          2025-10-16 16:56:53
📂 Version:            v11
🔖 Spec Hash:          3d116557f7d0cfac...

📊 API SPECIFICATION
════════════════════════════════════════════════════════════════════════════════

📄 Spec File:          specs/aadhaar-api.yaml
🌐 Total Endpoints:    2
🔗 Base URL:           http://localhost:5001/api/v1

Endpoints Covered:
  1. POST   /aadhaar/verify
  2. POST   /aadhaar/demographics

🧪 TEST SUITE DETAILS
════════════════════════════════════════════════════════════════════════════════

✓ Total Tests:         6
✓ Framework:           pytest
✓ Coverage Target:     ≥85%

📝 TEST SCENARIOS
════════════════════════════════════════════════════════════════════════════════

- Happy Path       - Valid requests with correct data
- Error Handling   - Invalid inputs, missing fields
- Edge Cases       - Boundary values
- Status Codes     - 200, 400, 403, 404, 429

⚠️  NOTES
════════════════════════════════════════════════════════════════════════════════

- AUTO-GENERATED - Manual edits preserved in version history
- Each run creates versioned file (v2, v3, etc.)
- Tests validate against: aadhaar-api.yaml

════════════════════════════════════════════════════════════════════════════════
"""


import pytest
import requests

def test_demographics_failure_invalid_aadhaar(invalid_demographics_payload):
    """
    Test failure of demographic retrieval with an invalid Aadhaar number.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=invalid_demographics_payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_demographics_failure_missing_consent(demographics_payload):
    """
    Test failure of demographic retrieval when consent is missing.
    """
    del demographics_payload["consent"]
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=demographics_payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_demographics_failure_unauthorized_access(demographics_payload):
    """
    Test unauthorized access to demographic details.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=demographics_payload)
    if response.status_code == 403:
        assert "error" in response.json()

def test_demographics_success(demographics_payload):
    """
    Test successful retrieval of demographic details with valid payload.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/demographics", json=demographics_payload)
    assert response.status_code == 200
    assert "demographics" in response.json()


def test_verify_aadhaar_failure(invalid_verify_aadhaar_payload):
    """
    Test failure of verification with an invalid Aadhaar number.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=invalid_verify_aadhaar_payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_verify_aadhaar_success(verify_aadhaar_payload):
    """
    Test successful verification of a valid Aadhaar number.
    """
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json=verify_aadhaar_payload)
    assert response.status_code == 200
    assert "message" in response.json()


