"""
Integration Example for New Dashboard Features
Shows how to emit new event types from main.py to the dashboard
"""

import requests
import json

DASHBOARD_URL = "http://localhost:5050/api/event"

def send_dashboard_event(event_type, data):
    """
    Send event to dashboard
    
    Args:
        event_type: Type of event (healing, error_analysis, api_diff, anomaly, traffic)
        data: Event data dictionary
    """
    try:
        payload = {'type': event_type, **data}
        response = requests.post(DASHBOARD_URL, json=payload, timeout=2)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send dashboard event: {e}")
        return False


# ============================================
# EXAMPLE 1: Self-Healing Event
# ============================================
def emit_healing_event(test_name, confidence, old_code, new_code):
    """
    Emit when a test is automatically healed
    
    Parameters:
        test_name: Name of the test that was healed
        confidence: Confidence score (0.0 to 1.0)
        old_code: Original test code
        new_code: Healed test code
    """
    healing_data = {
        'test_name': test_name,
        'confidence': confidence,
        'old_code': old_code,
        'new_code': new_code,
        'diff': {
            'before': old_code,
            'after': new_code
        },
        'timestamp': None  # Will be set by server
    }
    return send_dashboard_event('healing', healing_data)


# ============================================
# EXAMPLE 2: Error Analysis Event
# ============================================
def emit_error_analysis_event(test_name, error_type, message, root_cause, suggestions, request_data=None, response_data=None):
    """
    Emit when an error is analyzed
    
    Parameters:
        test_name: Name of the failing test
        error_type: Type of error (AssertionError, HTTPError, etc.)
        message: Error message
        root_cause: Identified root cause
        suggestions: List of fix suggestions
        request_data: Optional request details dict
        response_data: Optional response details dict
    """
    error_data = {
        'test_name': test_name,
        'error_type': error_type,
        'message': message,
        'root_cause': root_cause,
        'suggestions': suggestions,
        'timestamp': None
    }
    
    if request_data:
        error_data['request'] = request_data
    
    if response_data:
        error_data['response'] = response_data
    
    return send_dashboard_event('error_analysis', error_data)


# ============================================
# EXAMPLE 3: API Diff Event
# ============================================
def emit_api_diff_event(changes):
    """
    Emit when API specifications are compared
    
    Parameters:
        changes: List of change dictionaries, each containing:
            - type: 'added', 'removed', 'modified'
            - path: Endpoint or schema path
            - description: Human-readable description
            - breaking: Boolean indicating if breaking change
            - recommendation: Optional suggestion
    """
    diff_data = {
        'changes': changes
    }
    return send_dashboard_event('api_diff', diff_data)


# ============================================
# EXAMPLE 4: Anomaly Event
# ============================================
def emit_anomaly_event(endpoint, severity, anomaly_type, description, expected, actual):
    """
    Emit when an anomaly is detected
    
    Parameters:
        endpoint: API endpoint where anomaly was detected
        severity: 'critical', 'high', 'medium', 'low'
        anomaly_type: Type of anomaly (response_time, error_rate, etc.)
        description: Human-readable description
        expected: Expected value or baseline
        actual: Actual observed value
    """
    anomaly_data = {
        'endpoint': endpoint,
        'severity': severity,
        'type': anomaly_type,
        'description': description,
        'expected': expected,
        'actual': actual,
        'timestamp': None
    }
    return send_dashboard_event('anomaly', anomaly_data)


# ============================================
# EXAMPLE 5: Traffic Event
# ============================================
def emit_traffic_event(method, url, status_code, response_time=None):
    """
    Emit when traffic is recorded
    
    Parameters:
        method: HTTP method (GET, POST, etc.)
        url: Full URL
        status_code: HTTP status code
        response_time: Optional response time in ms
    """
    traffic_data = {
        'method': method,
        'url': url,
        'status_code': status_code,
        'timestamp': None
    }
    
    if response_time:
        traffic_data['response_time'] = response_time
    
    return send_dashboard_event('traffic', traffic_data)


# ============================================
# USAGE EXAMPLES IN main.py
# ============================================

def example_integration_in_main():
    """
    Example showing how to integrate into main.py POCOrchestrator
    """
    
    # Example 1: After self-healing
    if healing_result and healing_result['success']:
        emit_healing_event(
            test_name='test_auth_endpoint',
            confidence=healing_result['confidence'],
            old_code=healing_result['original_code'],
            new_code=healing_result['healed_code']
        )
    
    # Example 2: After error analysis
    if error_detail:
        emit_error_analysis_event(
            test_name='test_payment_api',
            error_type='AssertionError',
            message='Expected 200, got 401',
            root_cause='Missing authentication header',
            suggestions=[
                'Add Authorization header to request',
                'Check API key validity',
                'Verify authentication endpoint is working'
            ],
            request_data={
                'method': 'POST',
                'url': 'https://api.example.com/payment',
                'headers': {'Content-Type': 'application/json'}
            },
            response_data={
                'status_code': 401,
                'body': {'error': 'Unauthorized'}
            }
        )
    
    # Example 3: After API diff detection
    changes = [
        {
            'type': 'removed',
            'path': '/api/v1/deprecated',
            'description': 'Endpoint removed',
            'breaking': True,
            'recommendation': 'Migrate to /api/v2/new-endpoint'
        },
        {
            'type': 'added',
            'path': '/api/v2/new-feature',
            'description': 'New feature endpoint added',
            'breaking': False,
            'recommendation': 'Consider adding tests for new endpoint'
        }
    ]
    emit_api_diff_event(changes)
    
    # Example 4: After anomaly detection
    emit_anomaly_event(
        endpoint='/api/users',
        severity='high',
        anomaly_type='response_time',
        description='Response time 3x higher than baseline',
        expected='100ms',
        actual='350ms'
    )
    
    # Example 5: When recording traffic
    emit_traffic_event(
        method='POST',
        url='https://api.example.com/orders',
        status_code=201,
        response_time=45.2
    )


# ============================================
# COMPLETE INTEGRATION SNIPPET FOR main.py
# ============================================
"""
Add to main.py in POCOrchestrator class:

from dashboard_integration import (
    emit_healing_event,
    emit_error_analysis_event,
    emit_api_diff_event,
    emit_anomaly_event,
    emit_traffic_event
)

class POCOrchestrator:
    def __init__(self):
        # ... existing code ...
        from src.self_healing import SelfHealingEngine
        from src.error_analyzer import ErrorAnalyzer
        from src.api_diff import APIDiffDetector
        from src.anomaly_detector import AnomalyDetector
        from src.traffic_replay import TrafficRecorder
        
        self.healer = SelfHealingEngine()
        self.error_analyzer = ErrorAnalyzer()
        self.diff_detector = APIDiffDetector()
        self.anomaly_detector = AnomalyDetector()
        self.traffic_recorder = TrafficRecorder()
    
    def run_tests(self):
        # ... existing test execution ...
        
        # After test failures, try healing
        for failure in failures:
            healing_result = self.healer.heal_test(
                test_file=failure['file'],
                test_name=failure['name'],
                error_message=failure['error']
            )
            
            if healing_result:
                emit_healing_event(
                    test_name=failure['name'],
                    confidence=healing_result['confidence'],
                    old_code=healing_result['original_code'],
                    new_code=healing_result['healed_code']
                )
            
            # Analyze error
            error_detail = self.error_analyzer.analyze_failure(failure)
            emit_error_analysis_event(
                test_name=failure['name'],
                error_type=error_detail.error_type,
                message=error_detail.message,
                root_cause=error_detail.root_cause,
                suggestions=error_detail.suggestions
            )
        
        # Check for anomalies during execution
        for result in test_results:
            if result['response_time'] > threshold:
                anomaly = self.anomaly_detector.detect_response_time_anomaly(
                    endpoint=result['endpoint'],
                    response_time=result['response_time']
                )
                if anomaly:
                    emit_anomaly_event(
                        endpoint=anomaly.endpoint,
                        severity=anomaly.severity,
                        anomaly_type=anomaly.anomaly_type,
                        description=anomaly.description,
                        expected=anomaly.expected_value,
                        actual=anomaly.actual_value
                    )
"""

if __name__ == '__main__':
    print("Dashboard Integration Example")
    print("=" * 50)
    print("\nThis file shows how to send events to the dashboard.")
    print("\nEvent Types:")
    print("  - healing: Self-healing operations")
    print("  - error_analysis: Detailed error analysis")
    print("  - api_diff: API specification changes")
    print("  - anomaly: Detected anomalies")
    print("  - traffic: Recorded traffic")
    print("\nCopy the integration code into your main.py file.")
