"""
Import tests from Postman Collections and Insomnia exports
"""

import json
from typing import Dict, List
from pathlib import Path


class PostmanImporter:
    """
    Import Postman collections and convert to pytest tests
    """
    
    def __init__(self, collection_file: str):
        """
        Initialize Postman importer
        
        Args:
            collection_file: Path to Postman collection JSON file
        """
        self.collection_file = collection_file
        self.collection = self._load_collection()
    
    def _load_collection(self) -> Dict:
        """Load Postman collection"""
        with open(self.collection_file, 'r') as f:
            return json.load(f)
    
    def generate_tests(self) -> str:
        """
        Generate pytest tests from Postman collection
        
        Returns:
            Generated test code
        """
        lines = []
        lines.append("\"\"\"")
        lines.append(f"Tests generated from Postman collection: {self.collection.get('info', {}).get('name', 'Unknown')}")
        lines.append("\"\"\"")
        lines.append("")
        lines.append("import pytest")
        lines.append("from api.dummy_aadhaar_api import app")
        lines.append("")
        lines.append("@pytest.fixture")
        lines.append("def client():")
        lines.append("    return app.test_client()")
        lines.append("")
        
        # Process items (requests)
        items = self.collection.get('item', [])
        test_count = 0
        
        for item in items:
            if 'request' in item:
                test_code = self._generate_test_from_request(item, test_count + 1)
                if test_code:
                    lines.append(test_code)
                    lines.append("")
                    test_count += 1
            elif 'item' in item:  # Folder
                # Process nested items
                for nested_item in item['item']:
                    if 'request' in nested_item:
                        test_code = self._generate_test_from_request(nested_item, test_count + 1)
                        if test_code:
                            lines.append(test_code)
                            lines.append("")
                            test_count += 1
        
        return '\n'.join(lines)
    
    def _generate_test_from_request(self, item: Dict, index: int) -> str:
        """Generate test function from Postman request"""
        request = item.get('request', {})
        name = item.get('name', f'Request {index}')
        
        # Extract request details
        method = request.get('method', 'GET').lower()
        url = request.get('url', {})
        
        if isinstance(url, str):
            path = self._extract_path_from_url(url)
        elif isinstance(url, dict):
            raw_url = url.get('raw', '')
            path = self._extract_path_from_url(raw_url)
        else:
            return None
        
        # Generate test function
        test_name = self._sanitize_test_name(name)
        lines = []
        lines.append(f"def test_{test_name}_{index}(client):")
        lines.append(f"    \"\"\"")
        lines.append(f"    Test: {name}")
        lines.append(f"    Method: {method.upper()}")
        lines.append(f"    Path: {path}")
        lines.append(f"    \"\"\"")
        
        # Handle request body
        body = request.get('body', {})
        if body and method in ['post', 'put', 'patch']:
            raw_body = body.get('raw', '')
            if raw_body:
                try:
                    payload = json.loads(raw_body)
                    lines.append(f"    payload = {json.dumps(payload, indent=8)}")
                    lines.append(f"    response = client.{method}('{path}', json=payload)")
                except:
                    lines.append(f"    response = client.{method}('{path}')")
            else:
                lines.append(f"    response = client.{method}('{path}')")
        else:
            lines.append(f"    response = client.{method}('{path}')")
        
        # Add basic assertions
        lines.append("    assert response.status_code in [200, 201, 204]")
        
        # Check if there are tests defined in Postman
        tests = item.get('event', [])
        for test_event in tests:
            if test_event.get('listen') == 'test':
                script = test_event.get('script', {}).get('exec', [])
                # Try to extract assertions from Postman tests
                postman_assertions = self._extract_postman_assertions(script)
                for assertion in postman_assertions:
                    lines.append(f"    {assertion}")
        
        return '\n'.join(lines)
    
    def _extract_path_from_url(self, url: str) -> str:
        """Extract path from URL"""
        if not url:
            return '/'
        
        # Remove protocol and domain
        if '://' in url:
            url = url.split('://', 1)[1]
        
        if '/' in url:
            path = '/' + '/'.join(url.split('/')[1:])
        else:
            path = '/'
        
        # Remove query string
        if '?' in path:
            path = path.split('?')[0]
        
        return path or '/'
    
    def _sanitize_test_name(self, name: str) -> str:
        """Convert name to valid Python function name"""
        # Replace spaces and special characters
        sanitized = name.lower()
        sanitized = sanitized.replace(' ', '_')
        sanitized = sanitized.replace('-', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
        return sanitized
    
    def _extract_postman_assertions(self, script_lines: List[str]) -> List[str]:
        """Extract assertions from Postman test script"""
        assertions = []
        
        for line in script_lines:
            line = line.strip()
            
            # Convert common Postman assertions to pytest
            if 'pm.response.to.have.status' in line:
                # Extract status code
                try:
                    code = line.split('(')[1].split(')')[0]
                    assertions.append(f"assert response.status_code == {code}")
                except:
                    pass
            
            elif 'pm.response.json()' in line and 'to.have.property' in line:
                # Extract property check
                try:
                    prop = line.split("'")[1]
                    assertions.append(f"assert '{prop}' in response.get_json()")
                except:
                    pass
        
        return assertions
    
    def export_tests(self, output_file: str):
        """Export tests to file"""
        test_code = self.generate_tests()
        Path(output_file).write_text(test_code)


class InsomniaImporter:
    """
    Import Insomnia exports and convert to pytest tests
    """
    
    def __init__(self, export_file: str):
        """
        Initialize Insomnia importer
        
        Args:
            export_file: Path to Insomnia export JSON file
        """
        self.export_file = export_file
        self.export_data = self._load_export()
    
    def _load_export(self) -> Dict:
        """Load Insomnia export"""
        with open(self.export_file, 'r') as f:
            return json.load(f)
    
    def generate_tests(self) -> str:
        """
        Generate pytest tests from Insomnia export
        
        Returns:
            Generated test code
        """
        lines = []
        lines.append("\"\"\"")
        lines.append("Tests generated from Insomnia export")
        lines.append("\"\"\"")
        lines.append("")
        lines.append("import pytest")
        lines.append("from api.dummy_aadhaar_api import app")
        lines.append("")
        lines.append("@pytest.fixture")
        lines.append("def client():")
        lines.append("    return app.test_client()")
        lines.append("")
        
        # Filter request resources
        resources = self.export_data.get('resources', [])
        requests = [r for r in resources if r.get('_type') == 'request']
        
        for i, request in enumerate(requests, 1):
            test_code = self._generate_test_from_request(request, i)
            if test_code:
                lines.append(test_code)
                lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_test_from_request(self, request: Dict, index: int) -> str:
        """Generate test function from Insomnia request"""
        name = request.get('name', f'Request {index}')
        method = request.get('method', 'GET').lower()
        url = request.get('url', '')
        
        path = self._extract_path_from_url(url)
        
        test_name = self._sanitize_test_name(name)
        lines = []
        lines.append(f"def test_{test_name}_{index}(client):")
        lines.append(f"    \"\"\"")
        lines.append(f"    Test: {name}")
        lines.append(f"    Method: {method.upper()}")
        lines.append(f"    Path: {path}")
        lines.append(f"    \"\"\"")
        
        # Handle request body
        body = request.get('body', {})
        if body and method in ['post', 'put', 'patch']:
            body_text = body.get('text', '')
            if body_text:
                try:
                    payload = json.loads(body_text)
                    lines.append(f"    payload = {json.dumps(payload, indent=8)}")
                    lines.append(f"    response = client.{method}('{path}', json=payload)")
                except:
                    lines.append(f"    response = client.{method}('{path}')")
            else:
                lines.append(f"    response = client.{method}('{path}')")
        else:
            lines.append(f"    response = client.{method}('{path}')")
        
        # Add basic assertion
        lines.append("    assert response.status_code in [200, 201, 204]")
        
        return '\n'.join(lines)
    
    def _extract_path_from_url(self, url: str) -> str:
        """Extract path from URL"""
        if not url:
            return '/'
        
        # Remove protocol and domain
        if '://' in url:
            url = url.split('://', 1)[1]
        
        if '/' in url:
            path = '/' + '/'.join(url.split('/')[1:])
        else:
            path = '/'
        
        # Remove query string
        if '?' in path:
            path = path.split('?')[0]
        
        # Replace Insomnia variables {{variable}} with placeholder
        import re
        path = re.sub(r'\{\{.*?\}\}', '123456789012', path)
        
        return path or '/'
    
    def _sanitize_test_name(self, name: str) -> str:
        """Convert name to valid Python function name"""
        sanitized = name.lower()
        sanitized = sanitized.replace(' ', '_')
        sanitized = sanitized.replace('-', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
        return sanitized
    
    def export_tests(self, output_file: str):
        """Export tests to file"""
        test_code = self.generate_tests()
        Path(output_file).write_text(test_code)
