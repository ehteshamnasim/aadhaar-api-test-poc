"""
API Diff Detection System
Detects and visualizes changes between API versions
"""

import json
import yaml
from typing import Dict, List, Set, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class APIChange:
    """Represents a single API change"""
    change_type: str  # 'added', 'removed', 'modified'
    severity: str  # 'breaking', 'non-breaking', 'deprecated'
    category: str  # 'endpoint', 'parameter', 'response', 'schema'
    path: str
    description: str
    old_value: any = None
    new_value: any = None
    recommendation: str = None


class APIDiffDetector:
    """
    Detects differences between API specifications
    """
    
    def __init__(self):
        """Initialize API diff detector"""
        self.changes = []
        self.breaking_changes = []
        self.non_breaking_changes = []
        
    def compare_specs(self, old_spec_path: str, new_spec_path: str) -> Dict:
        """
        Compare two OpenAPI specifications
        
        Args:
            old_spec_path: Path to old spec file
            new_spec_path: Path to new spec file
            
        Returns:
            Dictionary containing all detected changes
        """
        # Load specifications
        old_spec = self._load_spec(old_spec_path)
        new_spec = self._load_spec(new_spec_path)
        
        # Reset changes
        self.changes = []
        self.breaking_changes = []
        self.non_breaking_changes = []
        
        # Compare different aspects
        self._compare_endpoints(old_spec, new_spec)
        self._compare_schemas(old_spec, new_spec)
        self._compare_parameters(old_spec, new_spec)
        self._compare_responses(old_spec, new_spec)
        
        # Categorize changes
        for change in self.changes:
            if change.severity == 'breaking':
                self.breaking_changes.append(change)
            else:
                self.non_breaking_changes.append(change)
        
        return {
            'summary': self._generate_summary(),
            'breaking_changes': [asdict(c) for c in self.breaking_changes],
            'non_breaking_changes': [asdict(c) for c in self.non_breaking_changes],
            'all_changes': [asdict(c) for c in self.changes],
            'impact_assessment': self._assess_impact()
        }
    
    def _load_spec(self, spec_path: str) -> Dict:
        """Load OpenAPI specification from file"""
        with open(spec_path, 'r') as f:
            if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def _compare_endpoints(self, old_spec: Dict, new_spec: Dict):
        """Compare API endpoints"""
        old_paths = set(old_spec.get('paths', {}).keys())
        new_paths = set(new_spec.get('paths', {}).keys())
        
        # Removed endpoints (breaking change)
        for path in old_paths - new_paths:
            self.changes.append(APIChange(
                change_type='removed',
                severity='breaking',
                category='endpoint',
                path=path,
                description=f"Endpoint {path} has been removed",
                old_value=path,
                recommendation="Update tests to remove references to this endpoint"
            ))
        
        # Added endpoints (non-breaking)
        for path in new_paths - old_paths:
            self.changes.append(APIChange(
                change_type='added',
                severity='non-breaking',
                category='endpoint',
                path=path,
                description=f"New endpoint {path} added",
                new_value=path,
                recommendation="Consider adding test coverage for this new endpoint"
            ))
        
        # Modified endpoints
        for path in old_paths & new_paths:
            old_methods = set(old_spec['paths'][path].keys())
            new_methods = set(new_spec['paths'][path].keys())
            
            # Removed HTTP methods (breaking)
            for method in old_methods - new_methods:
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    self.changes.append(APIChange(
                        change_type='removed',
                        severity='breaking',
                        category='endpoint',
                        path=f"{method.upper()} {path}",
                        description=f"HTTP method {method.upper()} removed from {path}",
                        old_value=method,
                        recommendation=f"Remove tests using {method.upper()} {path}"
                    ))
            
            # Added HTTP methods (non-breaking)
            for method in new_methods - old_methods:
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    self.changes.append(APIChange(
                        change_type='added',
                        severity='non-breaking',
                        category='endpoint',
                        path=f"{method.upper()} {path}",
                        description=f"HTTP method {method.upper()} added to {path}",
                        new_value=method,
                        recommendation=f"Add tests for {method.upper()} {path}"
                    ))
    
    def _compare_schemas(self, old_spec: Dict, new_spec: Dict):
        """Compare request/response schemas"""
        old_paths = old_spec.get('paths', {})
        new_paths = new_spec.get('paths', {})
        
        for path in set(old_paths.keys()) & set(new_paths.keys()):
            for method in set(old_paths[path].keys()) & set(new_paths[path].keys()):
                if method not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue
                
                old_endpoint = old_paths[path][method]
                new_endpoint = new_paths[path][method]
                
                # Compare request body schema
                old_req = old_endpoint.get('requestBody', {})
                new_req = new_endpoint.get('requestBody', {})
                
                self._compare_request_body(
                    f"{method.upper()} {path}",
                    old_req,
                    new_req
                )
    
    def _compare_request_body(self, endpoint: str, old_req: Dict, new_req: Dict):
        """Compare request body schemas"""
        # Check if required changed
        old_required = old_req.get('required', False)
        new_required = new_req.get('required', False)
        
        if not old_required and new_required:
            self.changes.append(APIChange(
                change_type='modified',
                severity='breaking',
                category='parameter',
                path=endpoint,
                description=f"Request body is now required for {endpoint}",
                old_value="optional",
                new_value="required",
                recommendation="Update tests to always include request body"
            ))
        
        # Compare schema properties
        old_schema = self._extract_schema(old_req)
        new_schema = self._extract_schema(new_req)
        
        if old_schema and new_schema:
            old_props = old_schema.get('properties', {})
            new_props = new_schema.get('properties', {})
            
            old_required_fields = set(old_schema.get('required', []))
            new_required_fields = set(new_schema.get('required', []))
            
            # Removed fields (breaking)
            for field in set(old_props.keys()) - set(new_props.keys()):
                self.changes.append(APIChange(
                    change_type='removed',
                    severity='breaking',
                    category='parameter',
                    path=f"{endpoint} > {field}",
                    description=f"Request field '{field}' removed",
                    old_value=old_props[field],
                    recommendation=f"Remove '{field}' from test payloads"
                ))
            
            # Added required fields (breaking)
            new_req_fields = new_required_fields - old_required_fields
            for field in new_req_fields:
                self.changes.append(APIChange(
                    change_type='modified',
                    severity='breaking',
                    category='parameter',
                    path=f"{endpoint} > {field}",
                    description=f"Field '{field}' is now required",
                    old_value="optional",
                    new_value="required",
                    recommendation=f"Add '{field}' to all test payloads for {endpoint}"
                ))
            
            # Added optional fields (non-breaking)
            for field in set(new_props.keys()) - set(old_props.keys()):
                if field not in new_required_fields:
                    self.changes.append(APIChange(
                        change_type='added',
                        severity='non-breaking',
                        category='parameter',
                        path=f"{endpoint} > {field}",
                        description=f"New optional field '{field}' added",
                        new_value=new_props[field],
                        recommendation=f"Consider testing with '{field}' field"
                    ))
    
    def _compare_parameters(self, old_spec: Dict, new_spec: Dict):
        """Compare query parameters and path parameters"""
        old_paths = old_spec.get('paths', {})
        new_paths = new_spec.get('paths', {})
        
        for path in set(old_paths.keys()) & set(new_paths.keys()):
            for method in set(old_paths[path].keys()) & set(new_paths[path].keys()):
                if method not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue
                
                old_params = old_paths[path][method].get('parameters', [])
                new_params = new_paths[path][method].get('parameters', [])
                
                old_param_names = {p['name']: p for p in old_params}
                new_param_names = {p['name']: p for p in new_params}
                
                endpoint = f"{method.upper()} {path}"
                
                # Removed parameters (breaking)
                for param_name in set(old_param_names.keys()) - set(new_param_names.keys()):
                    self.changes.append(APIChange(
                        change_type='removed',
                        severity='breaking',
                        category='parameter',
                        path=f"{endpoint} ? {param_name}",
                        description=f"Parameter '{param_name}' removed",
                        old_value=old_param_names[param_name],
                        recommendation=f"Remove '{param_name}' parameter from tests"
                    ))
                
                # Added required parameters (breaking)
                for param_name in set(new_param_names.keys()) - set(old_param_names.keys()):
                    param = new_param_names[param_name]
                    if param.get('required', False):
                        self.changes.append(APIChange(
                            change_type='added',
                            severity='breaking',
                            category='parameter',
                            path=f"{endpoint} ? {param_name}",
                            description=f"New required parameter '{param_name}' added",
                            new_value=param,
                            recommendation=f"Add '{param_name}' parameter to all tests"
                        ))
    
    def _compare_responses(self, old_spec: Dict, new_spec: Dict):
        """Compare response schemas"""
        old_paths = old_spec.get('paths', {})
        new_paths = new_spec.get('paths', {})
        
        for path in set(old_paths.keys()) & set(new_paths.keys()):
            for method in set(old_paths[path].keys()) & set(new_paths[path].keys()):
                if method not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue
                
                old_responses = old_paths[path][method].get('responses', {})
                new_responses = new_paths[path][method].get('responses', {})
                
                endpoint = f"{method.upper()} {path}"
                
                # Compare status codes
                old_codes = set(old_responses.keys())
                new_codes = set(new_responses.keys())
                
                # Removed status codes (breaking)
                for code in old_codes - new_codes:
                    self.changes.append(APIChange(
                        change_type='removed',
                        severity='breaking',
                        category='response',
                        path=f"{endpoint} → {code}",
                        description=f"Response code {code} removed",
                        old_value=code,
                        recommendation=f"Update tests expecting {code} response"
                    ))
                
                # Added status codes (non-breaking but noteworthy)
                for code in new_codes - old_codes:
                    self.changes.append(APIChange(
                        change_type='added',
                        severity='non-breaking',
                        category='response',
                        path=f"{endpoint} → {code}",
                        description=f"New response code {code} added",
                        new_value=code,
                        recommendation=f"Add tests for {code} response"
                    ))
                
                # Compare response schemas for common codes
                for code in old_codes & new_codes:
                    old_schema = self._extract_response_schema(old_responses[code])
                    new_schema = self._extract_response_schema(new_responses[code])
                    
                    if old_schema and new_schema:
                        self._compare_response_schema(
                            f"{endpoint} → {code}",
                            old_schema,
                            new_schema
                        )
    
    def _compare_response_schema(self, path: str, old_schema: Dict, new_schema: Dict):
        """Compare response schemas"""
        old_props = old_schema.get('properties', {})
        new_props = new_schema.get('properties', {})
        
        # Removed fields (breaking)
        for field in set(old_props.keys()) - set(new_props.keys()):
            self.changes.append(APIChange(
                change_type='removed',
                severity='breaking',
                category='response',
                path=f"{path} > {field}",
                description=f"Response field '{field}' removed",
                old_value=old_props[field],
                recommendation=f"Remove assertions checking '{field}' field"
            ))
        
        # Added fields (non-breaking)
        for field in set(new_props.keys()) - set(old_props.keys()):
            self.changes.append(APIChange(
                change_type='added',
                severity='non-breaking',
                category='response',
                path=f"{path} > {field}",
                description=f"New response field '{field}' added",
                new_value=new_props[field],
                recommendation=f"Consider validating '{field}' field"
            ))
        
        # Modified field types (breaking)
        for field in set(old_props.keys()) & set(new_props.keys()):
            old_type = old_props[field].get('type')
            new_type = new_props[field].get('type')
            
            if old_type != new_type:
                self.changes.append(APIChange(
                    change_type='modified',
                    severity='breaking',
                    category='response',
                    path=f"{path} > {field}",
                    description=f"Field '{field}' type changed from {old_type} to {new_type}",
                    old_value=old_type,
                    new_value=new_type,
                    recommendation=f"Update type assertions for '{field}' field"
                ))
    
    def _extract_schema(self, request_body: Dict) -> Dict:
        """Extract schema from request body"""
        if not request_body:
            return {}
        
        content = request_body.get('content', {})
        json_content = content.get('application/json', {})
        return json_content.get('schema', {})
    
    def _extract_response_schema(self, response: Dict) -> Dict:
        """Extract schema from response"""
        if not response:
            return {}
        
        content = response.get('content', {})
        json_content = content.get('application/json', {})
        return json_content.get('schema', {})
    
    def _generate_summary(self) -> Dict:
        """Generate summary of changes"""
        return {
            'total_changes': len(self.changes),
            'breaking_changes': len(self.breaking_changes),
            'non_breaking_changes': len(self.non_breaking_changes),
            'by_category': self._count_by_category(),
            'by_type': self._count_by_type()
        }
    
    def _count_by_category(self) -> Dict:
        """Count changes by category"""
        counts = {}
        for change in self.changes:
            counts[change.category] = counts.get(change.category, 0) + 1
        return counts
    
    def _count_by_type(self) -> Dict:
        """Count changes by type"""
        counts = {}
        for change in self.changes:
            counts[change.change_type] = counts.get(change.change_type, 0) + 1
        return counts
    
    def _assess_impact(self) -> Dict:
        """Assess overall impact of changes"""
        breaking_count = len(self.breaking_changes)
        
        if breaking_count == 0:
            risk_level = 'low'
            recommendation = 'Safe to update - no breaking changes detected'
        elif breaking_count <= 3:
            risk_level = 'medium'
            recommendation = 'Review breaking changes before updating'
        else:
            risk_level = 'high'
            recommendation = 'Significant breaking changes - thorough testing required'
        
        return {
            'risk_level': risk_level,
            'breaking_change_count': breaking_count,
            'recommendation': recommendation,
            'affected_tests_estimate': self._estimate_affected_tests()
        }
    
    def _estimate_affected_tests(self) -> int:
        """Estimate number of tests that might be affected"""
        # Simple heuristic: each breaking change affects ~2-3 tests on average
        return len(self.breaking_changes) * 2
    
    def generate_visual_diff(self) -> str:
        """Generate visual representation of changes"""
        lines = []
        lines.append("=" * 70)
        lines.append("API SPECIFICATION COMPARISON")
        lines.append("=" * 70)
        lines.append("")
        
        summary = self._generate_summary()
        lines.append(f"Total Changes: {summary['total_changes']}")
        lines.append(f"  Breaking: {summary['breaking_changes']}")
        lines.append(f"  Non-Breaking: {summary['non_breaking_changes']}")
        lines.append("")
        
        if self.breaking_changes:
            lines.append("BREAKING CHANGES:")
            lines.append("-" * 70)
            for change in self.breaking_changes:
                lines.append(f"  [{change.change_type.upper()}] {change.path}")
                lines.append(f"    {change.description}")
                if change.old_value:
                    lines.append(f"    - Old: {change.old_value}")
                if change.new_value:
                    lines.append(f"    + New: {change.new_value}")
                if change.recommendation:
                    lines.append(f"    → {change.recommendation}")
                lines.append("")
        
        if self.non_breaking_changes:
            lines.append("NON-BREAKING CHANGES:")
            lines.append("-" * 70)
            for change in self.non_breaking_changes:
                lines.append(f"  [{change.change_type.upper()}] {change.path}")
                lines.append(f"    {change.description}")
                if change.recommendation:
                    lines.append(f"    → {change.recommendation}")
                lines.append("")
        
        impact = self._assess_impact()
        lines.append("IMPACT ASSESSMENT:")
        lines.append("-" * 70)
        lines.append(f"  Risk Level: {impact['risk_level'].upper()}")
        lines.append(f"  Estimated Tests Affected: ~{impact['affected_tests_estimate']}")
        lines.append(f"  Recommendation: {impact['recommendation']}")
        lines.append("")
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def export_diff_report(self, output_file: str):
        """Export diff report to JSON file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(),
            'breaking_changes': [asdict(c) for c in self.breaking_changes],
            'non_breaking_changes': [asdict(c) for c in self.non_breaking_changes],
            'impact_assessment': self._assess_impact()
        }
        
        Path(output_file).write_text(json.dumps(report, indent=2))
