"""AI-Generated Tests v14 - 2025-10-17 02:40:45"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()


def test_generate_otp(client, input_data, expected_status, test_description):
    """Test /api/v1/aadhaar/otp/generate endpoint"""
    response = client.post('/api/v1/aadhaar/otp/generate', json=input_data)
    assert response.status_code == expected_status, f"Failed for: {test_description}"


def test_get_demographics(client, input_data, expected_status, test_description):
    """Test /api/v1/aadhaar/demographics endpoint"""
    response = client.post('/api/v1/aadhaar/demographics', json=input_data)
    assert response.status_code == expected_status, f"Failed for: {test_description}"


def test_perform_ekyc(client, input_data, expected_status, test_description):
    """Test /api/v1/aadhaar/ekyc endpoint"""
    response = client.post('/api/v1/aadhaar/ekyc', json=input_data)
    assert response.status_code == expected_status, f"Failed for: {test_description}"

def test_verify_aadhaar(client, input_data, expected_status, test_description):
    """Test /api/v1/aadhaar/verify endpoint"""
    response = client.post('/api/v1/aadhaar/verify', json=input_data)
    assert response.status_code == expected_status, f"Failed for: {test_description}"


def test_verify_otp(client, input_data, expected_status, test_description):
    """Test /api/v1/aadhaar/otp/verify endpoint"""
    response = client.post('/api/v1/aadhaar/otp/verify', json=input_data)
    assert response.status_code == expected_status, f"Failed for: {test_description}"

