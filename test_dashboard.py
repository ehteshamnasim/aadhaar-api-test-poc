#!/usr/bin/env python3
"""
Quick Test Script for Enhanced Dashboard
Sends sample events to test all new features
"""

import requests
import time
import json
from datetime import datetime

DASHBOARD_URL = "http://localhost:5050/api/event"

def send_event(event_type, data):
    """Send event to dashboard"""
    try:
        payload = {'type': event_type, **data}
        response = requests.post(DASHBOARD_URL, json=payload, timeout=2)
        if response.status_code == 200:
            print(f"✅ Sent {event_type} event")
            return True
        else:
            print(f"❌ Failed to send {event_type}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending {event_type}: {e}")
        return False

def test_healing_events():
    """Test self-healing events"""
    print("\n📋 Testing Self-Healing Events...")
    
    healings = [
        {
            'test_name': 'test_authentication_endpoint',
            'confidence': 0.95,
            'old_code': 'def test_auth():\n    assert response.status_code == 201',
            'new_code': 'def test_auth():\n    assert response.status_code == 200',
            'diff': {
                'before': 'assert response.status_code == 201',
                'after': 'assert response.status_code == 200'
            }
        },
        {
            'test_name': 'test_payment_api',
            'confidence': 0.88,
            'old_code': 'def test_payment():\n    assert data["amount"] == "100"',
            'new_code': 'def test_payment():\n    assert data["amount"] == 100',
            'diff': {
                'before': 'assert data["amount"] == "100"',
                'after': 'assert data["amount"] == 100'
            }
        },
        {
            'test_name': 'test_user_creation',
            'confidence': 0.72,
            'old_code': 'def test_user():\n    assert user.email',
            'new_code': 'def test_user():\n    assert user.email is not None',
            'diff': {
                'before': 'assert user.email',
                'after': 'assert user.email is not None'
            }
        }
    ]
    
    for healing in healings:
        send_event('healing', healing)
        time.sleep(0.5)

def test_error_analysis_events():
    """Test error analysis events"""
    print("\n🔍 Testing Error Analysis Events...")
    
    errors = [
        {
            'test_name': 'test_authentication',
            'error_type': 'AssertionError',
            'message': 'Expected status code 200, but got 401',
            'root_cause': 'Missing or invalid authentication token',
            'suggestions': [
                'Add Authorization header with valid token',
                'Check if token has expired',
                'Verify API key is correctly configured'
            ],
            'request': {
                'method': 'POST',
                'url': 'https://api.example.com/auth',
                'headers': {'Content-Type': 'application/json'}
            },
            'response': {
                'status_code': 401,
                'body': {'error': 'Unauthorized', 'message': 'Missing token'}
            }
        },
        {
            'test_name': 'test_data_validation',
            'error_type': 'ValidationError',
            'message': 'Field "email" is required',
            'root_cause': 'Request missing required field',
            'suggestions': [
                'Ensure email field is included in request body',
                'Validate request payload before sending',
                'Check API specification for required fields'
            ]
        },
        {
            'test_name': 'test_rate_limiting',
            'error_type': 'HTTPError',
            'message': 'Rate limit exceeded: 429 Too Many Requests',
            'root_cause': 'Too many requests in short time window',
            'suggestions': [
                'Add delay between requests',
                'Implement exponential backoff',
                'Use rate limiting headers to track remaining quota'
            ],
            'response': {
                'status_code': 429,
                'body': {'error': 'Rate limit exceeded'}
            }
        }
    ]
    
    for error in errors:
        send_event('error_analysis', error)
        time.sleep(0.5)

def test_api_diff_events():
    """Test API diff events"""
    print("\n🔄 Testing API Diff Events...")
    
    diff = {
        'changes': [
            {
                'type': 'removed',
                'path': '/api/v1/users/legacy',
                'description': 'Deprecated endpoint removed',
                'breaking': True,
                'recommendation': 'Migrate to /api/v2/users endpoint'
            },
            {
                'type': 'added',
                'path': '/api/v2/analytics',
                'description': 'New analytics endpoint added',
                'breaking': False,
                'recommendation': 'Consider adding tests for new endpoint'
            },
            {
                'type': 'modified',
                'path': '/api/v1/orders',
                'description': 'Response field "total" changed from string to number',
                'breaking': True,
                'recommendation': 'Update tests to expect number instead of string'
            },
            {
                'type': 'modified',
                'path': '/api/v1/products',
                'description': 'Added optional field "discount"',
                'breaking': False,
                'recommendation': 'Tests continue to work, consider testing new field'
            },
            {
                'type': 'added',
                'path': '/api/v2/subscriptions',
                'description': 'New subscription management endpoint',
                'breaking': False,
                'recommendation': 'Add comprehensive tests for subscription lifecycle'
            }
        ]
    }
    
    send_event('api_diff', diff)

def test_anomaly_events():
    """Test anomaly detection events"""
    print("\n⚠️  Testing Anomaly Events...")
    
    anomalies = [
        {
            'endpoint': '/api/users',
            'severity': 'critical',
            'type': 'response_time',
            'description': 'Response time exceeded 5x baseline',
            'expected': '120ms',
            'actual': '650ms'
        },
        {
            'endpoint': '/api/orders',
            'severity': 'high',
            'type': 'error_rate',
            'description': 'Error rate increased to 15%',
            'expected': '<2%',
            'actual': '15%'
        },
        {
            'endpoint': '/api/payments',
            'severity': 'critical',
            'type': 'unexpected_status',
            'description': 'Receiving 500 errors from payment gateway',
            'expected': '200',
            'actual': '500'
        },
        {
            'endpoint': '/api/search',
            'severity': 'medium',
            'type': 'response_time',
            'description': 'Response time slightly elevated',
            'expected': '200ms',
            'actual': '350ms'
        }
    ]
    
    for anomaly in anomalies:
        send_event('anomaly', anomaly)
        time.sleep(0.3)

def test_traffic_events():
    """Test traffic replay events"""
    print("\n🚦 Testing Traffic Events...")
    
    traffic = [
        {'method': 'GET', 'url': 'https://api.example.com/users/123', 'status_code': 200},
        {'method': 'POST', 'url': 'https://api.example.com/orders', 'status_code': 201},
        {'method': 'PUT', 'url': 'https://api.example.com/users/123/profile', 'status_code': 200},
        {'method': 'DELETE', 'url': 'https://api.example.com/sessions/abc', 'status_code': 204},
        {'method': 'GET', 'url': 'https://api.example.com/products?category=electronics', 'status_code': 200},
        {'method': 'POST', 'url': 'https://api.example.com/auth/login', 'status_code': 200},
        {'method': 'GET', 'url': 'https://api.example.com/orders/456', 'status_code': 404},
        {'method': 'POST', 'url': 'https://api.example.com/payments', 'status_code': 402},
        {'method': 'GET', 'url': 'https://api.example.com/analytics/dashboard', 'status_code': 200},
        {'method': 'PUT', 'url': 'https://api.example.com/settings', 'status_code': 200}
    ]
    
    for req in traffic:
        send_event('traffic', req)
        time.sleep(0.2)

def main():
    """Run all tests"""
    print("=" * 60)
    print("Dashboard Feature Test Script")
    print("=" * 60)
    print(f"\nTesting dashboard at: {DASHBOARD_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if dashboard is running
    print("\n🔍 Checking if dashboard is running...")
    try:
        response = requests.get("http://localhost:5050/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Dashboard is running")
        else:
            print("❌ Dashboard responded with error")
            return
    except Exception as e:
        print(f"❌ Cannot connect to dashboard: {e}")
        print("\n💡 Make sure dashboard is running:")
        print("   python dashboard/server.py")
        return
    
    # Run tests
    test_healing_events()
    time.sleep(1)
    
    test_error_analysis_events()
    time.sleep(1)
    
    test_api_diff_events()
    time.sleep(1)
    
    test_anomaly_events()
    time.sleep(1)
    
    test_traffic_events()
    
    print("\n" + "=" * 60)
    print("✅ All test events sent!")
    print("=" * 60)
    print("\n📊 Check dashboard at: http://localhost:5050")
    print("👉 Switch between tabs to see all features")
    print("🖱️  Click items to view details")

if __name__ == '__main__':
    main()
