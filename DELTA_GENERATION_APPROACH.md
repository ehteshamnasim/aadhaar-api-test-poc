# Delta Test Generation - Technical Approach

## Problem Statement
**Current Behavior:** POC regenerates ALL tests every time, even if only 1 endpoint changed  
**Desired Behavior:** Generate tests ONLY for new/modified endpoints (delta changes)

---

## Approach Overview

### High-Level Strategy
```
1. Store hash/signature of each endpoint from OpenAPI spec
2. Compare current spec with previous version
3. Identify: New endpoints, Modified endpoints, Deleted endpoints
4. Generate tests only for new/modified
5. Merge with existing test file
6. Update tracking database
```

---

## Technical Implementation

### Method 1: Git-Based Delta Detection (Recommended)

**Concept:** Use git diff to detect changes in OpenAPI spec

```python
import subprocess
import json
import hashlib

class DeltaDetector:
    def __init__(self, spec_path):
        self.spec_path = spec_path
        self.tracking_file = '.test_generation_tracking.json'
    
    def get_spec_changes(self):
        """
        Detect changes in OpenAPI spec using git diff
        """
        # Get git diff for spec file
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', self.spec_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # First run or not in git repo
            return self._full_scan()
        
        diff_output = result.stdout
        
        # Parse diff to find changed endpoints
        changed_paths = self._parse_diff(diff_output)
        
        return {
            'new': self._find_new_endpoints(changed_paths),
            'modified': self._find_modified_endpoints(changed_paths),
            'deleted': self._find_deleted_endpoints(changed_paths)
        }
    
    def _parse_diff(self, diff_output):
        """
        Parse git diff output to extract changed endpoint paths
        
        Example diff:
        +  /api/v1/new-endpoint:
        -  /api/v1/old-endpoint:
        """
        changes = {
            'added': [],
            'removed': [],
            'modified': []
        }
        
        for line in diff_output.split('\n'):
            if line.startswith('+ ') and '/api/' in line:
                path = self._extract_path(line)
                changes['added'].append(path)
            elif line.startswith('- ') and '/api/' in line:
                path = self._extract_path(line)
                changes['removed'].append(path)
        
        return changes
```

**Process Flow:**
```
Step 1: Git diff specs/api.yaml
  ↓
Step 2: Parse diff output
  ↓
Step 3: Extract changed endpoints
  ↓
Step 4: Generate tests only for those
  ↓
Step 5: Merge with existing test file
```

---

### Method 2: Hash-Based Tracking (Best for Non-Git)

**Concept:** Store hash of each endpoint definition, compare on each run

```python
import hashlib
import json
from pathlib import Path

class EndpointTracker:
    def __init__(self):
        self.tracking_file = Path('.endpoint_tracking.json')
        self.previous_state = self._load_tracking()
    
    def _load_tracking(self):
        """Load previous endpoint tracking state"""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_tracking(self, state):
        """Save current endpoint tracking state"""
        with open(self.tracking_file, 'w') as f:
            json.dump(state, indent=2, fp=f)
    
    def compute_endpoint_hash(self, endpoint):
        """
        Compute unique hash for endpoint definition
        
        Includes: path, method, parameters, request body, responses
        """
        # Create canonical representation
        canonical = json.dumps({
            'path': endpoint['path'],
            'method': endpoint['method'],
            'parameters': sorted(endpoint.get('parameters', []), key=str),
            'request_body': endpoint.get('request_body'),
            'responses': endpoint.get('responses')
        }, sort_keys=True)
        
        # Compute SHA256 hash
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def detect_changes(self, current_endpoints):
        """
        Compare current endpoints with previous state
        
        Returns: {
            'new': [...],        # Completely new endpoints
            'modified': [...],   # Existing endpoints with changes
            'unchanged': [...],  # No changes
            'deleted': [...]     # Removed endpoints
        }
        """
        current_state = {}
        changes = {
            'new': [],
            'modified': [],
            'unchanged': [],
            'deleted': []
        }
        
        # Process current endpoints
        for endpoint in current_endpoints:
            endpoint_id = f"{endpoint['method']} {endpoint['path']}"
            endpoint_hash = self.compute_endpoint_hash(endpoint)
            
            current_state[endpoint_id] = {
                'hash': endpoint_hash,
                'endpoint': endpoint
            }
            
            if endpoint_id not in self.previous_state:
                # New endpoint
                changes['new'].append(endpoint)
            elif self.previous_state[endpoint_id]['hash'] != endpoint_hash:
                # Modified endpoint
                changes['modified'].append(endpoint)
            else:
                # Unchanged endpoint
                changes['unchanged'].append(endpoint)
        
        # Find deleted endpoints
        for endpoint_id in self.previous_state:
            if endpoint_id not in current_state:
                changes['deleted'].append(self.previous_state[endpoint_id]['endpoint'])
        
        # Save current state for next run
        self._save_tracking(current_state)
        
        return changes

# Usage Example
tracker = EndpointTracker()
changes = tracker.detect_changes(parsed_spec['endpoints'])

print(f"New endpoints: {len(changes['new'])}")
print(f"Modified endpoints: {len(changes['modified'])}")
print(f"Unchanged endpoints: {len(changes['unchanged'])}")
print(f"Deleted endpoints: {len(changes['deleted'])}")
```

**Tracking File Format (.endpoint_tracking.json):**
```json
{
  "POST /api/v1/verify": {
    "hash": "a1b2c3d4e5f6...",
    "endpoint": {
      "path": "/api/v1/verify",
      "method": "POST",
      "summary": "Verify Aadhaar"
    }
  },
  "GET /api/v1/status/{request_id}": {
    "hash": "f6e5d4c3b2a1...",
    "endpoint": {
      "path": "/api/v1/status/{request_id}",
      "method": "GET",
      "summary": "Check status"
    }
  }
}
```

---

### Method 3: Timestamp-Based Detection

**Concept:** Track last modification time of spec file and test files

```python
import os
from datetime import datetime

class TimestampTracker:
    def __init__(self, spec_path, test_dir):
        self.spec_path = spec_path
        self.test_dir = test_dir
    
    def needs_regeneration(self):
        """
        Check if spec is newer than test files
        """
        spec_mtime = os.path.getmtime(self.spec_path)
        
        # Find all test files
        test_files = Path(self.test_dir).glob('test_*.py')
        
        for test_file in test_files:
            test_mtime = os.path.getmtime(test_file)
            
            # If spec is newer, regeneration needed
            if spec_mtime > test_mtime:
                return True
        
        return False
    
    def get_spec_version(self):
        """
        Get version info from spec file
        """
        with open(self.spec_path) as f:
            spec = yaml.safe_load(f)
        
        return {
            'version': spec.get('info', {}).get('version'),
            'modified': datetime.fromtimestamp(os.path.getmtime(self.spec_path))
        }
```

**Limitation:** Doesn't identify WHICH endpoints changed, only that spec changed

---

## Test File Merging Strategy

### Approach: AST-Based Test Merging

**Concept:** Parse existing test file, add/update only changed tests

```python
import ast

class TestMerger:
    def __init__(self, existing_test_file):
        self.existing_file = existing_test_file
        self.existing_tests = self._parse_existing_tests()
    
    def _parse_existing_tests(self):
        """
        Parse existing test file and extract test functions
        """
        if not Path(self.existing_file).exists():
            return {}
        
        with open(self.existing_file, 'r') as f:
            code = f.read()
        
        tree = ast.parse(code)
        tests = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Extract test function
                test_code = ast.get_source_segment(code, node)
                tests[node.name] = test_code
        
        return tests
    
    def merge_tests(self, new_tests_dict):
        """
        Merge new tests with existing tests
        
        Args:
            new_tests_dict: {
                'test_verify_aadhaar': 'def test_verify_aadhaar...',
                'test_new_endpoint': 'def test_new_endpoint...'
            }
        
        Returns:
            Complete merged test file content
        """
        merged = {}
        
        # Keep unchanged existing tests
        for test_name, test_code in self.existing_tests.items():
            if test_name not in new_tests_dict:
                merged[test_name] = test_code
        
        # Add/update with new tests
        for test_name, test_code in new_tests_dict.items():
            merged[test_name] = test_code
        
        # Generate complete file
        return self._generate_file(merged)
    
    def _generate_file(self, tests):
        """
        Generate complete test file with imports and fixtures
        """
        imports = """
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
"""
        
        test_functions = '\n\n'.join(tests.values())
        
        return f"{imports}\n\n{test_functions}\n"
```

---

## Complete Delta Generation Flow

### Integrated Approach

```python
class DeltaTestGenerator:
    def __init__(self, spec_path, test_file):
        self.spec_path = spec_path
        self.test_file = test_file
        self.tracker = EndpointTracker()
        self.merger = TestMerger(test_file)
        self.llm_generator = TestGenerator()
    
    def generate_delta_tests(self):
        """
        Main delta generation pipeline
        """
        # Step 1: Parse current OpenAPI spec
        parser = OpenAPIParser(self.spec_path)
        current_endpoints = parser.to_dict()['endpoints']
        
        # Step 2: Detect changes
        changes = self.tracker.detect_changes(current_endpoints)
        
        # Step 3: Send dashboard event
        send_event('delta_analysis', {
            'new': len(changes['new']),
            'modified': len(changes['modified']),
            'unchanged': len(changes['unchanged']),
            'deleted': len(changes['deleted'])
        })
        
        # Step 4: Generate tests only for new/modified
        endpoints_to_generate = changes['new'] + changes['modified']
        
        if not endpoints_to_generate:
            send_event('generate', {
                'status': 'skipped',
                'message': 'No changes detected - skipping test generation'
            })
            return self.test_file
        
        # Step 5: Generate tests using LLM (only for changed endpoints)
        new_tests = {}
        for idx, endpoint in enumerate(endpoints_to_generate):
            send_event('test_created', {
                'test_number': idx + 1,
                'test_name': self._get_test_name(endpoint),
                'reason': 'new' if endpoint in changes['new'] else 'modified'
            })
            
            # Generate test code
            test_code = self.llm_generator.generate_single_test(endpoint)
            test_name = self._get_test_name(endpoint)
            new_tests[test_name] = test_code
        
        # Step 6: Merge with existing tests
        merged_content = self.merger.merge_tests(new_tests)
        
        # Step 7: Handle deleted endpoints
        if changes['deleted']:
            merged_content = self._remove_deleted_tests(
                merged_content, 
                changes['deleted']
            )
        
        # Step 8: Write merged file
        with open(self.test_file, 'w') as f:
            f.write(merged_content)
        
        # Step 9: Send completion event
        send_event('generate', {
            'status': 'success',
            'count': len(new_tests),
            'total_tests': len(new_tests) + len(changes['unchanged']),
            'new': len(changes['new']),
            'modified': len(changes['modified']),
            'deleted': len(changes['deleted'])
        })
        
        return self.test_file
    
    def _get_test_name(self, endpoint):
        """
        Generate test function name from endpoint
        
        Example:
            POST /api/v1/verify -> test_verify_aadhaar_post
        """
        path_parts = endpoint['path'].strip('/').split('/')
        method = endpoint['method'].lower()
        name = '_'.join(path_parts + [method])
        return f"test_{name}"
    
    def _remove_deleted_tests(self, content, deleted_endpoints):
        """
        Remove tests for deleted endpoints from merged content
        """
        tree = ast.parse(content)
        
        # Find tests to remove
        tests_to_remove = set()
        for endpoint in deleted_endpoints:
            test_name = self._get_test_name(endpoint)
            tests_to_remove.add(test_name)
        
        # Filter out deleted tests
        # (Implementation using AST manipulation)
        
        return filtered_content
```

---

## Dashboard Integration

### New Event Types for Delta Generation

```python
# Event 1: Delta Analysis
send_event('delta_analysis', {
    'new': 2,
    'modified': 1,
    'unchanged': 12,
    'deleted': 0
})

# Event 2: Test Creation with Reason
send_event('test_created', {
    'test_number': 1,
    'test_name': 'test_new_endpoint',
    'reason': 'new',  # or 'modified'
    'endpoint': 'POST /api/v1/new-endpoint'
})

# Event 3: Generation Complete with Delta Info
send_event('generate', {
    'status': 'success',
    'count': 3,           # New/modified tests generated
    'total_tests': 15,    # Total tests in file after merge
    'new': 2,
    'modified': 1,
    'deleted': 0,
    'unchanged': 12
})
```

### Dashboard Display

```javascript
// app.js - Delta Analysis Display
case 'delta_analysis':
    document.getElementById('delta-new').textContent = data.new;
    document.getElementById('delta-modified').textContent = data.modified;
    document.getElementById('delta-unchanged').textContent = data.unchanged;
    
    if (data.new === 0 && data.modified === 0) {
        addLog('No endpoint changes detected - test generation skipped', 'info');
    } else {
        addLog(`Delta detected: ${data.new} new, ${data.modified} modified endpoints`, 'success');
    }
    break;

case 'test_created':
    const badge = data.reason === 'new' ? 
        '<span class="badge-new">NEW</span>' : 
        '<span class="badge-modified">MODIFIED</span>';
    addLog(`${badge} Generated test ${data.test_number}: ${data.test_name}`, 'info');
    break;
```

---

## Performance Comparison

### Before (Full Regeneration):
```
5 endpoints → Generate 5 tests → 30 seconds
5 endpoints (no changes) → Generate 5 tests → 30 seconds  ❌ Wasteful
```

### After (Delta Generation):
```
5 endpoints → Generate 5 tests → 30 seconds
5 endpoints (no changes) → Skip generation → 2 seconds  ✅ Efficient
5 endpoints + 1 new → Generate 1 test → 8 seconds  ✅ Fast
```

**Performance Gain:**
- **No changes:** 93% faster (2s vs 30s)
- **1 new endpoint:** 73% faster (8s vs 30s)
- **Partial changes:** Linear scaling

---

## Implementation Steps

### Phase 1: Add Tracking (Week 1)
1. Create `EndpointTracker` class
2. Add `.endpoint_tracking.json` to `.gitignore`
3. Integrate with `main.py`

### Phase 2: Delta Detection (Week 1)
1. Implement `detect_changes()` method
2. Add dashboard events for delta analysis
3. Test with sample spec changes

### Phase 3: Selective Generation (Week 2)
1. Modify `TestGenerator` to accept single endpoint
2. Implement `generate_single_test()` method
3. Update LLM prompt for single endpoint

### Phase 4: Test Merging (Week 2)
1. Create `TestMerger` class
2. Implement AST-based merging
3. Handle deleted endpoints

### Phase 5: Dashboard Updates (Week 3)
1. Add delta metrics to UI
2. Show NEW/MODIFIED badges
3. Update activity log messages

### Phase 6: Testing & Refinement (Week 3)
1. Test with various change scenarios
2. Handle edge cases
3. Performance benchmarking

---

## Edge Cases to Handle

### 1. First Run (No Tracking File)
```python
if not self.tracking_file.exists():
    # Full generation on first run
    return {'new': all_endpoints, 'modified': [], 'unchanged': []}
```

### 2. Spec File Deleted
```python
if not Path(self.spec_path).exists():
    raise FileNotFoundError(f"Spec file not found: {self.spec_path}")
```

### 3. Corrupted Tracking File
```python
try:
    state = json.load(f)
except json.JSONDecodeError:
    # Reset tracking, do full scan
    return self._full_scan()
```

### 4. Endpoint Renamed (Appears as Delete + Add)
```python
def detect_renames(self, changes):
    """
    Detect renamed endpoints by comparing hashes
    If hash matches but ID changed → rename (not delete+add)
    """
    # Advanced logic to detect renames
    pass
```

### 5. Test File Manually Modified
```python
def validate_existing_tests(self):
    """
    Check if existing tests are still valid
    If manually modified, preserve those changes
    """
    pass
```

---

## Configuration Options

### Add to `config.yaml`:

```yaml
delta_generation:
  enabled: true
  tracking_file: '.endpoint_tracking.json'
  
  # Strategy: 'hash', 'git', 'timestamp'
  strategy: 'hash'
  
  # Merge strategy: 'preserve', 'overwrite'
  merge_strategy: 'preserve'
  
  # Clean deleted tests
  auto_cleanup: true
  
  # Force full regeneration
  force_full: false
```

---

## CLI Integration

### Add Command-Line Flag:

```bash
# Delta generation (default)
python main.py specs/api.yaml

# Force full regeneration
python main.py specs/api.yaml --full

# Show delta without generating
python main.py specs/api.yaml --dry-run

# Reset tracking
python main.py specs/api.yaml --reset-tracking
```

```python
# main.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('spec', help='OpenAPI spec file')
parser.add_argument('--full', action='store_true', help='Force full regeneration')
parser.add_argument('--dry-run', action='store_true', help='Show changes without generating')
parser.add_argument('--reset-tracking', action='store_true', help='Reset endpoint tracking')

args = parser.parse_args()

if args.full:
    orchestrator.generate_all_tests()
else:
    orchestrator.generate_delta_tests()
```

---

## Benefits of Delta Generation

### 1. **Speed**
- 70-95% faster for partial changes
- 2 seconds vs 30 seconds for no changes

### 2. **Cost Savings**
- Fewer LLM API calls
- Reduced compute resources
- Lower Ollama processing time

### 3. **Stability**
- Existing tests remain unchanged
- Manual modifications preserved
- Less churn in test files

### 4. **Git-Friendly**
- Smaller diffs in commits
- Easier code reviews
- Clear change history

### 5. **CI/CD Efficiency**
- Faster pipeline execution
- Fewer test file changes
- Reduced merge conflicts

---

## Recommended Approach

**Best Implementation:** **Hash-Based Tracking (Method 2)**

**Why?**
✅ Works without git  
✅ Precise endpoint-level detection  
✅ Handles all change types (new, modified, deleted)  
✅ Simple to implement  
✅ No external dependencies  

**When to use Git-Based (Method 1)?**
- Already in git workflow
- Want spec version history
- Need blame/audit trail

**When to use Timestamp (Method 3)?**
- Quick prototype
- Don't need endpoint-level precision
- Acceptable to regenerate all on any change

---

## Next Steps

1. **Choose Strategy:** Hash-based recommended
2. **Implement Tracker:** Create `EndpointTracker` class
3. **Update Generator:** Add delta detection to POC
4. **Test Thoroughly:** Various change scenarios
5. **Update Dashboard:** Show delta metrics
6. **Document:** Update README with delta feature

---

## Code Structure

```
src/
├── delta_tracker.py         # EndpointTracker class
├── test_merger.py           # TestMerger class
├── test_generator.py        # Updated with generate_single_test()
└── delta_generator.py       # DeltaTestGenerator orchestration

.endpoint_tracking.json      # Tracking state (gitignored)

config.yaml                  # Delta configuration
```

---

## Conclusion

**Delta test generation is a critical optimization for production use.**

**Implementation Complexity:** Medium  
**Performance Gain:** 70-95%  
**Recommended Timeline:** 3 weeks  
**Priority:** High for scaling to large APIs

Would save significant time and resources in real-world scenarios with large API specs!
