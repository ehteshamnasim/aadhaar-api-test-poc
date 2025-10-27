"""
Production Traffic Recorder and Replayer
Capture real API calls and replay them in tests
"""

import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class TrafficRecord:
    """Recorded API traffic"""
    timestamp: str
    method: str
    url: str
    headers: Dict[str, str]
    request_body: Optional[Dict] = None
    response_status: int = None
    response_body: Optional[Dict] = None
    response_time_ms: float = None
    session_id: Optional[str] = None


class TrafficRecorder:
    """
    Records API traffic for later replay
    """
    
    def __init__(self, output_dir: str = 'traffic_recordings'):
        """
        Initialize traffic recorder
        
        Args:
            output_dir: Directory to store recordings
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.recordings = []
        self.sensitive_headers = {'authorization', 'cookie', 'x-api-key', 'token'}
        self.sensitive_fields = {'password', 'secret', 'api_key', 'token', 'credit_card'}
    
    def record(self, method: str, url: str, headers: Dict, 
              request_body: Dict = None, response_status: int = None,
              response_body: Dict = None, response_time_ms: float = None,
              session_id: str = None):
        """
        Record an API call
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            request_body: Request body
            response_status: Response status code
            response_body: Response body
            response_time_ms: Response time
            session_id: Session identifier
        """
        # Mask sensitive data
        masked_headers = self._mask_headers(headers)
        masked_request = self._mask_sensitive_data(request_body) if request_body else None
        masked_response = self._mask_sensitive_data(response_body) if response_body else None
        
        record = TrafficRecord(
            timestamp=datetime.now().isoformat(),
            method=method,
            url=url,
            headers=masked_headers,
            request_body=masked_request,
            response_status=response_status,
            response_body=masked_response,
            response_time_ms=response_time_ms,
            session_id=session_id
        )
        
        self.recordings.append(record)
    
    def _mask_headers(self, headers: Dict) -> Dict:
        """Mask sensitive headers"""
        masked = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                masked[key] = '***MASKED***'
            else:
                masked[key] = value
        return masked
    
    def _mask_sensitive_data(self, data: Dict) -> Dict:
        """Mask sensitive fields in request/response body"""
        if not isinstance(data, dict):
            return data
        
        masked = {}
        for key, value in data.items():
            if key.lower() in self.sensitive_fields:
                masked[key] = '***MASKED***'
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_data(value)
            elif isinstance(value, list):
                masked[key] = [self._mask_sensitive_data(item) if isinstance(item, dict) else item 
                              for item in value]
            else:
                masked[key] = value
        return masked
    
    def save_recording(self, filename: str = None):
        """
        Save recordings to file
        
        Args:
            filename: Output filename (auto-generated if not provided)
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'traffic_{timestamp}.json'
        
        output_path = self.output_dir / filename
        
        data = {
            'recording_timestamp': datetime.now().isoformat(),
            'total_requests': len(self.recordings),
            'recordings': [asdict(r) for r in self.recordings]
        }
        
        output_path.write_text(json.dumps(data, indent=2))
        return str(output_path)


class TrafficReplayer:
    """
    Replays recorded API traffic as tests
    """
    
    def __init__(self, recording_file: str):
        """
        Initialize traffic replayer
        
        Args:
            recording_file: Path to traffic recording file
        """
        self.recording_file = recording_file
        self.recordings = self._load_recordings()
    
    def _load_recordings(self) -> List[TrafficRecord]:
        """Load recordings from file"""
        with open(self.recording_file, 'r') as f:
            data = json.load(f)
        
        return [TrafficRecord(**r) for r in data['recordings']]
    
    def generate_test_code(self, base_url: str = None) -> str:
        """
        Generate pytest test code from recordings
        
        Args:
            base_url: Base URL for API (if different from recording)
            
        Returns:
            Generated test code
        """
        lines = []
        lines.append("import pytest")
        lines.append("from api.dummy_aadhaar_api import app")
        lines.append("")
        lines.append("@pytest.fixture")
        lines.append("def client():")
        lines.append("    return app.test_client()")
        lines.append("")
        
        for i, record in enumerate(self.recordings, 1):
            test_name = self._generate_test_name(record, i)
            lines.append(f"def {test_name}(client):")
            lines.append(f"    \"\"\"")
            lines.append(f"    Replay of recorded traffic from {record.timestamp}")
            lines.append(f"    Original: {record.method} {record.url}")
            lines.append(f"    \"\"\"")
            
            # Extract path from URL
            path = self._extract_path(record.url)
            
            # Generate request
            if record.request_body:
                lines.append(f"    payload = {json.dumps(record.request_body, indent=8)}")
                lines.append(f"    response = client.{record.method.lower()}('{path}', json=payload)")
            else:
                lines.append(f"    response = client.{record.method.lower()}('{path}')")
            
            # Generate assertions
            if record.response_status:
                lines.append(f"    assert response.status_code == {record.response_status}")
            
            if record.response_body:
                lines.append("    data = response.get_json()")
                for key in record.response_body.keys():
                    if key not in ['***MASKED***']:
                        lines.append(f"    assert '{key}' in data")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_test_name(self, record: TrafficRecord, index: int) -> str:
        """Generate test function name from record"""
        # Extract endpoint name
        path = self._extract_path(record.url)
        endpoint = path.replace('/', '_').replace('-', '_').strip('_')
        method = record.method.lower()
        
        return f"test_replay_{method}_{endpoint}_{index}"
    
    def _extract_path(self, url: str) -> str:
        """Extract path from full URL"""
        # Remove scheme and domain
        if '://' in url:
            url = url.split('://', 1)[1]
        if '/' in url:
            path = '/' + url.split('/', 1)[1]
        else:
            path = '/'
        
        # Remove query string
        if '?' in path:
            path = path.split('?')[0]
        
        return path
    
    def export_test_file(self, output_file: str):
        """
        Export generated tests to file
        
        Args:
            output_file: Output file path
        """
        test_code = self.generate_test_code()
        Path(output_file).write_text(test_code)
