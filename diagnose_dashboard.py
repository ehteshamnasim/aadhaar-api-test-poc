#!/usr/bin/env python3
"""
Quick diagnostic test to check dashboard connectivity
"""

import requests
import time

DASHBOARD_URL = "http://localhost:5050"

print("🔍 Dashboard Diagnostic Test\n")
print("=" * 50)

# Test 1: Check if dashboard is running
print("\n1. Testing dashboard connection...")
try:
    response = requests.get(f"{DASHBOARD_URL}", timeout=2)
    print(f"   ✓ Dashboard is running (status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Dashboard not accessible: {e}")
    print(f"   → Start dashboard: python3 start_dashboard.py")
    exit(1)

# Test 2: Send a simple event
print("\n2. Testing event endpoint...")
try:
    response = requests.post(
        f"{DASHBOARD_URL}/api/event",
        json={'type': 'status', 'message': 'Test event'},
        timeout=2
    )
    print(f"   ✓ Event endpoint works (status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Event endpoint failed: {e}")

# Test 3: Send test execution event with details
print("\n3. Sending test execution event...")
try:
    test_data = {
        'type': 'execute',
        'passed': 5,
        'failed': 2,
        'total': 7,
        'details': [
            {'name': 'test_generate_otp', 'passed': True, 'reason': 'All assertions passed'},
            {'name': 'test_verify_otp', 'passed': True, 'reason': 'All assertions passed'},
            {'name': 'test_invalid_otp', 'passed': False, 'reason': 'assert 400 == 200'},
            {'name': 'test_demographics', 'passed': True, 'reason': 'All assertions passed'},
            {'name': 'test_biometric', 'passed': True, 'reason': 'All assertions passed'},
            {'name': 'test_timeout', 'passed': False, 'reason': 'Connection timeout'},
            {'name': 'test_ekyc', 'passed': True, 'reason': 'All assertions passed'}
        ]
    }
    response = requests.post(
        f"{DASHBOARD_URL}/api/event",
        json=test_data,
        timeout=2
    )
    print(f"   ✓ Test execution event sent (status: {response.status_code})")
    print(f"   → Check dashboard Overview tab for test details")
except Exception as e:
    print(f"   ✗ Failed to send test event: {e}")

# Test 4: Send healing event
print("\n4. Sending self-healing event...")
try:
    healing_data = {
        'type': 'healing',
        'test_name': 'test_invalid_otp',
        'confidence': 0.85,
        'old_code': 'assert response.status_code == 400',
        'new_code': 'assert response.status_code == 200',
        'diff': {
            'before': 'assert response.status_code == 400',
            'after': 'assert response.status_code == 200'
        }
    }
    response = requests.post(
        f"{DASHBOARD_URL}/api/event",
        json=healing_data,
        timeout=2
    )
    print(f"   ✓ Healing event sent (status: {response.status_code})")
    print(f"   → Check dashboard Self-Healing tab")
except Exception as e:
    print(f"   ✗ Failed to send healing event: {e}")

# Test 5: Send error analysis event
print("\n5. Sending error analysis event...")
try:
    error_data = {
        'type': 'error_analysis',
        'test_name': 'test_invalid_otp',
        'error_type': 'AssertionError',
        'message': 'assert 400 == 200',
        'root_cause': 'Expected error response but received success status',
        'suggestions': [
            'Update test assertion to match actual API behavior',
            'Verify API specification for correct status codes',
            'Check if API endpoint logic changed'
        ]
    }
    response = requests.post(
        f"{DASHBOARD_URL}/api/event",
        json=error_data,
        timeout=2
    )
    print(f"   ✓ Error analysis event sent (status: {response.status_code})")
    print(f"   → Check dashboard Error Analysis tab")
except Exception as e:
    print(f"   ✗ Failed to send error event: {e}")

# Test 6: Send API diff event
print("\n6. Sending API diff event...")
try:
    diff_data = {
        'type': 'api_diff',
        'changes': [
            {
                'type': 'added',
                'path': '/api/v1/aadhaar/face-auth',
                'description': 'New endpoint added: /api/v1/aadhaar/face-auth',
                'breaking': False,
                'recommendation': 'Add test coverage for new endpoint'
            },
            {
                'type': 'modified',
                'path': '/api/v1/aadhaar/verify-otp',
                'description': 'Endpoint modified: /api/v1/aadhaar/verify-otp',
                'breaking': False,
                'recommendation': 'Review and update test assertions'
            },
            {
                'type': 'removed',
                'path': '/api/v1/aadhaar/legacy-verify',
                'description': 'Endpoint removed: /api/v1/aadhaar/legacy-verify',
                'breaking': True,
                'recommendation': 'Remove or update tests for removed endpoint'
            }
        ]
    }
    response = requests.post(
        f"{DASHBOARD_URL}/api/event",
        json=diff_data,
        timeout=2
    )
    print(f"   ✓ API diff event sent (status: {response.status_code})")
    print(f"   → Check dashboard API Diff tab")
except Exception as e:
    print(f"   ✗ Failed to send diff event: {e}")

# Test 7: Send anomaly event
print("\n7. Sending anomaly event...")
try:
    anomaly_data = {
        'type': 'anomaly',
        'endpoint': 'Overall Test Suite',
        'severity': 'high',
        'anomaly_type': 'error_rate',
        'description': 'High test failure rate detected: 28.6%',
        'expected': '<20% failure rate',
        'actual': '28.6% (2/7 tests failed)'
    }
    response = requests.post(
        f"{DASHBOARD_URL}/api/event",
        json=anomaly_data,
        timeout=2
    )
    print(f"   ✓ Anomaly event sent (status: {response.status_code})")
    print(f"   → Check dashboard Anomalies tab")
except Exception as e:
    print(f"   ✗ Failed to send anomaly event: {e}")

print("\n" + "=" * 50)
print("\n✅ Diagnostic complete!")
print("\n📋 Next steps:")
print("   1. Open dashboard: http://localhost:5050")
print("   2. Check all 5 tabs for data")
print("   3. If tabs are empty, check browser console for errors")
print("   4. Try refreshing the dashboard page")
print("\n")
