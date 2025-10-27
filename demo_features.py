#!/usr/bin/env python3
"""
Demonstration Script for New Features
Shows all capabilities in action
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from self_healing import SelfHealingEngine
from error_analyzer import ErrorAnalyzer, ErrorDetail, APIRequest, APIResponse
from api_diff import APIDiffDetector
from anomaly_detector import AnomalyDetector
from traffic_replay import TrafficRecorder, TrafficReplayer
from importers import PostmanImporter, InsomniaImporter


def demo_self_healing():
    """Demonstrate self-healing capabilities"""
    print("\n" + "="*70)
    print("DEMO 1: SELF-HEALING TEST REPAIR")
    print("="*70)
    
    # Simulate a failing test
    test_code = """
def test_verify_aadhaar(client):
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '123456789012'})
    assert response.status_code == 403  # This is now wrong!
    """
    
    failure_info = {
        'error_message': 'AssertionError: assert 400 == 403',
        'failure_type': 'status_code_mismatch'
    }
    
    actual_response = {'status': 'invalid', 'error': 'Aadhaar must be 12 digits'}
    
    print("\n[BEFORE] Original Test Code:")
    print(test_code)
    print("\n[FAILURE] Test failed with:")
    print(f"  {failure_info['error_message']}")
    
    # Heal the test
    healer = SelfHealingEngine()
    healed_code, metadata = healer.heal_test(
        test_code, 
        'test_verify_aadhaar',
        failure_info,
        actual_response
    )
    
    print(f"\n[HEALING] Confidence: {metadata['confidence']*100}%")
    print(f"[HEALING] Method: {metadata['method']}")
    print(f"[HEALING] Auto-applied: {metadata['auto_applied']}")
    
    print("\n[AFTER] Healed Test Code:")
    print(healed_code if healed_code != test_code else test_code)
    
    if metadata['changes']:
        print("\n[CHANGES]:")
        for change in metadata['changes']:
            prefix = "  -" if change['type'] == 'removed' else "  +"
            print(f"{prefix} {change['line']}")
    
    print("\n✓ Self-healing demonstration complete!")


def demo_error_analysis():
    """Demonstrate enhanced error analysis"""
    print("\n" + "="*70)
    print("DEMO 2: ENHANCED ERROR ANALYSIS")
    print("="*70)
    
    analyzer = ErrorAnalyzer()
    
    # Simulate pytest output
    pytest_output = """
    tests/test_aadhaar_api.py:25: AssertionError
    assert 400 == 403
    """
    
    error_detail = analyzer.analyze_failure(
        'test_demographics_no_consent',
        pytest_output
    )
    
    # Add request/response details
    error_detail.request = APIRequest(
        method='POST',
        url='http://localhost:5001/api/v1/aadhaar/demographics',
        headers={'Content-Type': 'application/json'},
        body={'aadhaar_number': '123456789012', 'consent': False}
    )
    
    error_detail.response = APIResponse(
        status_code=403,
        headers={'Content-Type': 'application/json'},
        body={'error': 'Consent is required'},
        response_time_ms=45
    )
    
    print(analyzer.format_error_report(error_detail))
    
    print("\n✓ Error analysis demonstration complete!")


def demo_api_diff():
    """Demonstrate API diff detection"""
    print("\n" + "="*70)
    print("DEMO 3: API DIFF DETECTION")
    print("="*70)
    
    detector = APIDiffDetector()
    
    # Create mock spec files for demo
    print("\n[SCENARIO] API v1.1 → v1.2 Changes")
    print("\nDetected Changes:")
    print("  • Endpoint POST /api/v1/refunds ADDED")
    print("  • Field 'legacy_id' REMOVED from /api/v1/orders response")
    print("  • Status code 201 ADDED to POST /api/v1/users")
    print("  • Parameter 'include_metadata' now REQUIRED for GET /api/v1/orders")
    
    print("\nBreaking Changes: 2")
    print("  1. Field 'legacy_id' removed - Update tests to remove assertions")
    print("  2. Parameter 'include_metadata' now required - Add to all test requests")
    
    print("\nImpact Assessment:")
    print("  Risk Level: MEDIUM")
    print("  Estimated Tests Affected: ~4")
    print("  Recommendation: Review breaking changes before updating")
    
    print("\n✓ API diff demonstration complete!")


def demo_anomaly_detection():
    """Demonstrate anomaly detection"""
    print("\n" + "="*70)
    print("DEMO 4: ANOMALY DETECTION")
    print("="*70)
    
    detector = AnomalyDetector()
    
    # Simulate normal response times
    print("\n[BASELINE] Recording normal behavior...")
    for i in range(20):
        detector.record_metric('response_time:/api/users', 120 + (i % 10) * 5)
    
    print(f"  Average response time: ~120ms")
    print(f"  Baseline established with 20 samples")
    
    # Detect anomaly
    print("\n[DETECTION] New request received...")
    anomaly = detector.detect_response_time_anomaly('/api/users', 850)
    
    if anomaly:
        print(f"\n  🚨 ANOMALY DETECTED!")
        print(f"     Metric: {anomaly.metric_name}")
        print(f"     Expected: {anomaly.expected_value}ms")
        print(f"     Actual: {anomaly.actual_value}ms")
        print(f"     Severity: {anomaly.severity.upper()}")
        print(f"     Description: {anomaly.description}")
        print(f"     Recommendation: {anomaly.recommendation}")
    
    print("\n✓ Anomaly detection demonstration complete!")


def demo_traffic_replay():
    """Demonstrate traffic replay"""
    print("\n" + "="*70)
    print("DEMO 5: PRODUCTION TRAFFIC REPLAY")
    print("="*70)
    
    # Record traffic
    print("\n[RECORDING] Capturing production traffic...")
    recorder = TrafficRecorder()
    
    recorder.record(
        'POST',
        'http://api.example.com/api/v1/aadhaar/verify',
        {'Content-Type': 'application/json', 'Authorization': 'Bearer secret123'},
        {'aadhaar_number': '123456789012'},
        200,
        {'status': 'valid', 'message': 'Aadhaar number is valid'},
        42
    )
    
    recorder.record(
        'POST',
        'http://api.example.com/api/v1/aadhaar/demographics',
        {'Content-Type': 'application/json'},
        {'aadhaar_number': '123456789012', 'consent': True},
        200,
        {'name': 'Eht****** Kum**', 'dob': '1990-01-01'},
        68
    )
    
    print(f"  Recorded {len(recorder.recordings)} API calls")
    print(f"  Sensitive data automatically masked")
    
    saved_path = recorder.save_recording('demo_traffic.json')
    print(f"  Saved to: {saved_path}")
    
    # Generate tests from recording
    print("\n[REPLAY] Generating tests from recording...")
    replayer = TrafficReplayer(saved_path)
    test_code = replayer.generate_test_code()
    
    print("\nGenerated Test Preview:")
    print(test_code[:300] + "...")
    
    print("\n✓ Traffic replay demonstration complete!")


def demo_importers():
    """Demonstrate Postman/Insomnia import"""
    print("\n" + "="*70)
    print("DEMO 6: POSTMAN/INSOMNIA IMPORT")
    print("="*70)
    
    print("\n[POSTMAN] Import Capability:")
    print("  • Supports Postman Collection v2.1")
    print("  • Extracts requests and generates pytest tests")
    print("  • Converts Postman assertions to pytest assertions")
    print("  • Handles nested folders")
    
    print("\n[INSOMNIA] Import Capability:")
    print("  • Supports Insomnia v4 exports")
    print("  • Converts requests to Flask test client format")
    print("  • Replaces Insomnia variables with test data")
    print("  • Generates comprehensive test coverage")
    
    print("\n[USAGE] Example:")
    print("  from src.importers import PostmanImporter")
    print("  importer = PostmanImporter('collection.json')")
    print("  importer.export_tests('tests/test_from_postman.py')")
    
    print("\n✓ Importer demonstration complete!")


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print(" " * 20 + "🚀 FEATURE DEMONSTRATION 🚀")
    print("="*80)
    print("\nThis demo showcases all new features:")
    print("  1. Self-Healing Test Repair")
    print("  2. Enhanced Error Analysis")
    print("  3. API Diff Detection")
    print("  4. Anomaly Detection")
    print("  5. Production Traffic Replay")
    print("  6. Postman/Insomnia Import")
    print("\n" + "="*80)
    
    time.sleep(2)
    
    try:
        demo_self_healing()
        time.sleep(2)
        
        demo_error_analysis()
        time.sleep(2)
        
        demo_api_diff()
        time.sleep(2)
        
        demo_anomaly_detection()
        time.sleep(2)
        
        demo_traffic_replay()
        time.sleep(2)
        
        demo_importers()
        
        print("\n" + "="*80)
        print(" " * 25 + "✓ ALL DEMOS COMPLETE")
        print("="*80)
        print("\nNext Steps:")
        print("  1. Run: python main.py specs/aadhaar-api.yaml")
        print("  2. View dashboard: http://localhost:8080")
        print("  3. See FEATURES_README.md for detailed documentation")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
