import requests
import time
from typing import Dict, List, Tuple

class ContractTester:
    """Test if API implementation matches OpenAPI spec (Contract Testing)"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
    
    def test_contracts(self, endpoints: List[Dict]) -> List[Dict]:
        """Test all endpoints against their contracts"""
        print("\n🔍 Running Contract Tests...")
        
        for endpoint in endpoints:
            result = self._test_endpoint_contract(endpoint)
            self.results.append(result)
            
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"{status} {endpoint['method']} {endpoint['path']}")
            if not result['passed']:
                print(f"   Error: {result['error']}")
        
        return self.results
    
    def _test_endpoint_contract(self, endpoint: Dict) -> Dict:
        """Test single endpoint contract"""
        method = endpoint['method']
        path = endpoint['path']
        url = self.base_url + path
        
        result = {
            'endpoint': f"{method} {path}",
            'passed': False,
            'error': None,
            'status_code': None
        }
        
        # Retry logic for flaky API
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Prepare sample request
                sample_payload = self._create_sample_payload(endpoint)
                
                # Make request
                response = requests.request(
                    method=method,
                    url=url,
                    json=sample_payload if method in ['POST', 'PUT', 'PATCH'] else None,
                    timeout=10  # Increased timeout
                )
                
                result['status_code'] = response.status_code
                
                # Check if status code matches spec
                expected_codes = list(endpoint['responses'].keys())
                
                if str(response.status_code) in expected_codes:
                    result['passed'] = True
                    return result  # Success - return immediately
                else:
                    result['error'] = f"Got {response.status_code}, expected one of {expected_codes}"
                    # Don't return yet - might be temporary
            
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    print(f"    Retry {attempt + 1}/{max_retries} for {method} {path}")
                    time.sleep(1)  # Wait before retry
                    continue
                result['error'] = f"Connection failed after {max_retries} attempts: {str(e)}"
            except requests.exceptions.Timeout:
                result['error'] = "Request timeout (10s)"
            except Exception as e:
                result['error'] = f"Unexpected error: {str(e)}"
                break
        
        return result
    
    def _create_sample_payload(self, endpoint: Dict) -> Dict:
        """Create sample payload from schema"""
        request_body = endpoint.get('request_body', {})
        properties = request_body.get('properties', {})
        
        if not properties:
            return {}
        
        # Create sample payload based on schema
        payload = {}
        for field, schema in properties.items():
            field_type = schema.get('type', 'string')
            example = schema.get('example')
            
            if example:
                payload[field] = example
            elif field_type == 'string':
                pattern = schema.get('pattern', '')
                if 'aadhaar' in field.lower():
                    payload[field] = '123456789012'  # Valid test Aadhaar
                else:
                    payload[field] = 'sample_value'
            elif field_type == 'boolean':
                payload[field] = True
            elif field_type == 'integer':
                payload[field] = 1
            elif field_type == 'number':
                payload[field] = 1.0
        
        return payload
    
    def get_summary(self) -> Dict:
        """Get summary of contract test results"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        }

if __name__ == '__main__':
    from parser import OpenAPIParser
    
    parser = OpenAPIParser('specs/aadhaar-api.yaml')
    parsed_spec = parser.to_dict()
    
    tester = ContractTester(parsed_spec['base_url'])
    results = tester.test_contracts(parsed_spec['endpoints'])
    
    print("\n" + "="*50)
    summary = tester.get_summary()
    print(f"Contract Tests: {summary['passed']}/{summary['total']} passed ({summary['pass_rate']:.1f}%)")