import yaml
from typing import Dict, List, Any

class OpenAPIParser:
    """Parse OpenAPI specification"""
    
    def __init__(self, spec_path: str):
        self.spec_path = spec_path
        self.spec = self._load_spec()
    
    def _load_spec(self) -> Dict:
        """Load YAML spec file"""
        with open(self.spec_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_base_url(self) -> str:
        """Get base URL from spec"""
        servers = self.spec.get('servers', [])
        if servers:
            return servers[0].get('url', 'http://localhost:5000')
        return 'http://localhost:5000'
    
    def get_endpoints(self) -> List[Dict[str, Any]]:
        """Extract all endpoints with details"""
        endpoints = []
        paths = self.spec.get('paths', {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'request_body': self._parse_request_body(details.get('requestBody')),
                        'responses': self._parse_responses(details.get('responses', {})),
                        'parameters': details.get('parameters', [])
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_request_body(self, request_body: Dict) -> Dict:
        """Parse request body schema"""
        if not request_body:
            return {}
        
        content = request_body.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})
        
        return {
            'required': request_body.get('required', False),
            'properties': schema.get('properties', {}),
            'required_fields': schema.get('required', [])
        }
    
    def _parse_responses(self, responses: Dict) -> Dict:
        """Parse response definitions"""
        parsed_responses = {}
        
        for status_code, response_def in responses.items():
            parsed_responses[status_code] = {
                'description': response_def.get('description', ''),
                'schema': self._get_response_schema(response_def)
            }
        
        return parsed_responses
    
    def _get_response_schema(self, response_def: Dict) -> Dict:
        """Get response schema"""
        content = response_def.get('content', {})
        json_content = content.get('application/json', {})
        return json_content.get('schema', {})
    
    def to_dict(self) -> Dict:
        """Convert parsed data to dictionary"""
        return {
            'base_url': self.get_base_url(),
            'endpoints': self.get_endpoints()
        }

if __name__ == '__main__':
    parser = OpenAPIParser('specs/aadhaar-api.yaml')
    print("Base URL:", parser.get_base_url())
    print("\nEndpoints found:")
    for ep in parser.get_endpoints():
        print(f"  {ep['method']} {ep['path']}: {ep['summary']}")