#!/usr/bin/env python3
"""
Quick diagnostic test to check dashboard connectivity
"""
import requests
import sys
import time

DASHBOARD_URL = "http://localhost:5050"

def check_dashboard_health():
    """Check if dashboard is running"""
    print("🔍 Checking dashboard health...")
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Dashboard is running!")
            return True
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard. Is it running?")
        print("   Start it with: python3 dashboard/server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_test_event():
    """Send a simple test event"""
    print("\n📤 Sending test healing event...")
    try:
        payload = {
            'type': 'healing',
            'test_name': 'test_quick_check',
            'confidence': 0.95,
            'old_code': 'assert x == 1',
            'new_code': 'assert x == 2',
            'diff': {
                'before': 'assert x == 1',
                'after': 'assert x == 2'
            },
            'timestamp': time.time()
        }
        
        response = requests.post(f"{DASHBOARD_URL}/api/event", json=payload, timeout=2)
        
        if response.status_code == 200:
            print("✅ Event sent successfully!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to send event: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending event: {e}")
        return False

def main():
    print("="*60)
    print("🔧 Dashboard Quick Test")
    print("="*60)
    
    # Check dashboard health
    if not check_dashboard_health():
        sys.exit(1)
    
    # Send test event
    if not send_test_event():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ All checks passed!")
    print("="*60)
    print("\n📊 Next steps:")
    print("   1. Open http://localhost:5050 in your browser")
    print("   2. Click on 'Self-Healing' tab")
    print("   3. You should see 'test_quick_check' in the list")
    print("\n   If you don't see it:")
    print("   - Check browser console (F12) for JavaScript errors")
    print("   - Check dashboard/server.py terminal for Python errors")
    print("="*60)

if __name__ == '__main__':
    main()
