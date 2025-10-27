"""
Anomaly Detection System
ML-based detection of unusual API behavior
"""

import json
import statistics
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict


@dataclass
class Metric:
    """Performance metric"""
    timestamp: str
    value: float
    context: Dict = None


@dataclass
class Anomaly:
    """Detected anomaly"""
    timestamp: str
    metric_name: str
    expected_value: float
    actual_value: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    recommendation: str


class AnomalyDetector:
    """
    Detects anomalies in API behavior using statistical methods
    """
    
    def __init__(self, window_size: int = 100):
        """
        Initialize anomaly detector
        
        Args:
            window_size: Number of data points to keep for baseline calculation
        """
        self.window_size = window_size
        self.metrics = defaultdict(lambda: deque(maxlen=window_size))
        self.anomalies = []
        self.thresholds = {
            'response_time': {
                'multiplier': 3.0,  # 3x standard deviation
                'absolute_max_ms': 5000
            },
            'error_rate': {
                'max_percentage': 5.0
            },
            'status_code': {
                'unexpected_codes': [500, 502, 503, 504]
            }
        }
    
    def record_metric(self, metric_name: str, value: float, context: Dict = None):
        """
        Record a metric value
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            context: Additional context (endpoint, method, etc.)
        """
        metric = Metric(
            timestamp=datetime.now().isoformat(),
            value=value,
            context=context or {}
        )
        self.metrics[metric_name].append(metric)
    
    def detect_response_time_anomaly(self, endpoint: str, response_time_ms: float) -> Optional[Anomaly]:
        """
        Detect if response time is anomalous
        
        Args:
            endpoint: API endpoint
            response_time_ms: Response time in milliseconds
            
        Returns:
            Anomaly if detected, None otherwise
        """
        metric_name = f"response_time:{endpoint}"
        self.record_metric(metric_name, response_time_ms, {'endpoint': endpoint})
        
        # Need at least 10 samples for baseline
        if len(self.metrics[metric_name]) < 10:
            return None
        
        # Calculate baseline statistics
        values = [m.value for m in self.metrics[metric_name]]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Check if current value is anomalous
        threshold = mean + (self.thresholds['response_time']['multiplier'] * stdev)
        
        if response_time_ms > threshold or response_time_ms > self.thresholds['response_time']['absolute_max_ms']:
            severity = self._calculate_severity(
                response_time_ms,
                mean,
                self.thresholds['response_time']['absolute_max_ms']
            )
            
            anomaly = Anomaly(
                timestamp=datetime.now().isoformat(),
                metric_name=metric_name,
                expected_value=round(mean, 2),
                actual_value=round(response_time_ms, 2),
                severity=severity,
                description=f"Response time for {endpoint} is {round(response_time_ms - mean, 2)}ms above normal",
                recommendation=self._get_response_time_recommendation(severity)
            )
            
            self.anomalies.append(anomaly)
            return anomaly
        
        return None
    
    def detect_error_rate_anomaly(self, endpoint: str, error_count: int, total_count: int) -> Optional[Anomaly]:
        """
        Detect if error rate is anomalous
        
        Args:
            endpoint: API endpoint
            error_count: Number of errors
            total_count: Total number of requests
            
        Returns:
            Anomaly if detected, None otherwise
        """
        if total_count == 0:
            return None
        
        error_rate = (error_count / total_count) * 100
        metric_name = f"error_rate:{endpoint}"
        self.record_metric(metric_name, error_rate, {'endpoint': endpoint})
        
        max_error_rate = self.thresholds['error_rate']['max_percentage']
        
        if error_rate > max_error_rate:
            severity = 'critical' if error_rate > 20 else 'high' if error_rate > 10 else 'medium'
            
            anomaly = Anomaly(
                timestamp=datetime.now().isoformat(),
                metric_name=metric_name,
                expected_value=max_error_rate,
                actual_value=round(error_rate, 2),
                severity=severity,
                description=f"Error rate for {endpoint} is {round(error_rate, 2)}% (threshold: {max_error_rate}%)",
                recommendation="Investigate recent changes, check logs, and verify API health"
            )
            
            self.anomalies.append(anomaly)
            return anomaly
        
        return None
    
    def detect_unexpected_status_code(self, endpoint: str, status_code: int) -> Optional[Anomaly]:
        """
        Detect unexpected status codes
        
        Args:
            endpoint: API endpoint
            status_code: HTTP status code
            
        Returns:
            Anomaly if detected, None otherwise
        """
        unexpected_codes = self.thresholds['status_code']['unexpected_codes']
        
        if status_code in unexpected_codes:
            anomaly = Anomaly(
                timestamp=datetime.now().isoformat(),
                metric_name=f"status_code:{endpoint}",
                expected_value=200,
                actual_value=status_code,
                severity='high',
                description=f"Endpoint {endpoint} returned {status_code} (server error)",
                recommendation="Check API server logs and health status immediately"
            )
            
            self.anomalies.append(anomaly)
            return anomaly
        
        return None
    
    def _calculate_severity(self, actual: float, expected: float, max_value: float) -> str:
        """Calculate severity based on deviation"""
        if actual > max_value:
            return 'critical'
        
        deviation = abs(actual - expected) / expected if expected > 0 else 0
        
        if deviation > 3.0:  # 300% deviation
            return 'critical'
        elif deviation > 2.0:  # 200% deviation
            return 'high'
        elif deviation > 1.0:  # 100% deviation
            return 'medium'
        else:
            return 'low'
    
    def _get_response_time_recommendation(self, severity: str) -> str:
        """Get recommendation based on severity"""
        recommendations = {
            'low': "Monitor the situation",
            'medium': "Investigate recent changes and check API load",
            'high': "Review API performance, check database queries and external dependencies",
            'critical': "Immediate action required - check for issues in production environment"
        }
        return recommendations.get(severity, "Monitor the situation")
    
    def get_anomaly_summary(self) -> Dict:
        """Get summary of detected anomalies"""
        if not self.anomalies:
            return {
                'total_anomalies': 0,
                'by_severity': {},
                'recent_anomalies': []
            }
        
        by_severity = defaultdict(int)
        for anomaly in self.anomalies:
            by_severity[anomaly.severity] += 1
        
        # Get recent anomalies (last 10)
        recent = sorted(self.anomalies, key=lambda a: a.timestamp, reverse=True)[:10]
        
        return {
            'total_anomalies': len(self.anomalies),
            'by_severity': dict(by_severity),
            'recent_anomalies': [asdict(a) for a in recent]
        }
    
    def export_anomaly_report(self, output_file: str):
        """Export anomaly report to JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': self.get_anomaly_summary(),
            'all_anomalies': [asdict(a) for a in self.anomalies]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
