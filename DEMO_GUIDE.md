# Demo Guide - AI-Powered API Test Automation

## What It Does
Automatically generates and runs API tests from OpenAPI specs using AI (Ollama), validates them, and provides real-time feedback via dashboard.

---

## System Flow

```
OpenAPI Spec → AI Test Generator → Pytest Execution → Dashboard + Git
     ↓              ↓                    ↓                ↓
  Parse        Generate Tests      Run & Validate    Show Results
  Validate     (Ollama AI)        (Coverage 85%+)    Auto-commit
```

---

## Step-by-Step Demo Flow

### Step 1: Parse OpenAPI Spec
**What happens:**
- Reads `specs/aadhaar-api.yaml`
- Extracts endpoints, methods, parameters, schemas
- Detects spec changes via hash

**Uses:**
- `src/parser.py` - OpenAPI parser
- MD5 hashing for change detection

**Prerequisites:**
- Valid OpenAPI 3.0+ YAML file
- Well-formed schemas and endpoint definitions

**Risks:**
- Invalid YAML syntax → Fix: Validate YAML before running
- Missing required fields → Fix: Ensure complete spec
- **Impact:** Medium | **Likelihood:** Low

---

### Step 2: Generate Tests with AI
**What happens:**
- Sends spec to Ollama (llama3:70b)
- AI generates pytest code
- Creates versioned file: `test_aadhaar_api_v{N}.py`

**Uses:**
- `src/test_generator.py` - AI test generator
- Ollama API at `http://localhost:11434`
- llama3:70b model (~40GB)

**Prerequisites:**
- Ollama running: `ollama serve`
- Model downloaded: `ollama pull llama3:70b`
- 32GB+ RAM for llama3:70b (or use llama3:8b with 8GB RAM)
- Network connectivity to Ollama

**Risks:**
- Ollama not running → Fix: Start `ollama serve`
- Model not downloaded → Fix: Pull model first
- Insufficient RAM → Fix: Use smaller model (llama3:8b)
- AI generates invalid syntax → Automatic retry with corrections
- **Impact:** High | **Likelihood:** Medium

---

### Step 3: Validate Generated Tests
**What happens:**
- Syntax validation (AST parsing)
- Import verification
- Code compilation check

**Uses:**
- `src/validator.py` - Code validator
- Python AST module

**Prerequisites:**
- Valid Python 3.8+ installation
- Required test dependencies installed

**Risks:**
- Import errors → Auto-fixed in retry
- Syntax errors → Auto-fixed in retry
- **Impact:** Low | **Likelihood:** Low (auto-healing)

---

### Step 4: Run Contract Testing
**What happens:**
- Validates spec against dummy API
- Checks endpoints exist
- Verifies response schemas match

**Uses:**
- `src/contract_tester.py` - Contract validator
- `api/dummy_aadhaar_api.py` - Mock API server

**Prerequisites:**
- Dummy API running on port 5001
- API implements all spec endpoints
- Network connectivity to API

**Risks:**
- API not running → Fix: Start `python api/dummy_aadhaar_api.py`
- Port conflicts → Fix: Change port in config
- Schema mismatch → Fix: Update API or spec
- **Impact:** High | **Likelihood:** Medium

---

### Step 5: Execute Tests with Coverage
**What happens:**
- Runs pytest with coverage
- Captures pass/fail/error counts
- Generates HTML coverage report
- Validates 85%+ coverage threshold

**Uses:**
- pytest with pytest-cov plugin
- JSON reporter for accuracy
- HTML coverage reports in `htmlcov/`

**Prerequisites:**
- pytest and pytest-cov installed
- Test dependencies available
- Dummy API running and responsive

**Risks:**
- Connection failures → Retry logic handles
- Assertion failures → Reported in detail
- Coverage below 85% → Warns user
- Network timeouts → Fix: Increase timeout settings
- **Impact:** Medium | **Likelihood:** Low

---

### Step 6: Display Results on Dashboard
**What happens:**
- Real-time events via SSE
- Shows progress, test counts, failures
- Links to coverage reports

**Uses:**
- `dashboard/server.py` - Flask dashboard
- Server-Sent Events (SSE)
- `dashboard/index.html` - UI

**Prerequisites:**
- Dashboard running: `python start_dashboard.py`
- Port 8080 available
- Modern browser with SSE support

**Risks:**
- Dashboard not running → Stats still saved locally
- Port conflict → Change port in config
- Browser compatibility → Use Chrome/Firefox
- **Impact:** Low | **Likelihood:** Low (non-critical)

---

### Step 7: Git Auto-Commit
**What happens:**
- Auto-commits generated tests
- Commits coverage reports
- Pushes to remote (optional)

**Uses:**
- `src/git_committer.py` - Git automation
- Git CLI commands

**Prerequisites:**
- Git repository initialized
- Git user configured
- Clean working directory (no conflicts)
- Remote repository configured (for push)

**Risks:**
- Merge conflicts → Manual resolution needed
- Uncommitted changes → Prompt user to commit
- Network issues → Push fails, retry later
- **Impact:** Low | **Likelihood:** Low

---

## Quick Demo Commands

### Terminal 1: Start Ollama
```bash
ollama serve
```
**Leave running**

### Terminal 2: Start Dummy API
```bash
python api/dummy_aadhaar_api.py
```
**API runs on port 5001**

### Terminal 3: Start Dashboard
```bash
python start_dashboard.py
```
**Open http://localhost:8080**

### Terminal 4: Run Demo
```bash
python main.py
```

---

## Success Criteria

| Deliverable | Success Metric | Verification |
|-------------|---------------|--------------|
| Spec Parsing | All endpoints extracted | Check dashboard logs |
| Test Generation | Valid pytest file created | File exists in `tests/` |
| Validation | No syntax/import errors | Validator passes |
| Contract Testing | All endpoints match spec | Contract report shows 100% |
| Test Execution | 85%+ coverage | Coverage report in `htmlcov/` |
| Dashboard | Real-time updates visible | UI shows progress |
| Git Commit | Tests committed | Check `git log` |

---

## Common Demo Issues & Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Ollama connection refused" | Run `ollama serve` in Terminal 1 |
| "Model not found" | Run `ollama pull llama3:70b` |
| "API connection refused" | Start dummy API in Terminal 2 |
| "Dashboard not loading" | Check port 8080 not in use |
| "Tests fail with 404" | Verify API running on port 5001 |
| "Coverage below 85%" | AI will retry with better tests |

---

## Resource Requirements

**Minimum:**
- 16GB RAM (for llama3:8b)
- 20GB disk space
- Python 3.8+

**Recommended:**
- 32GB RAM (for llama3:70b)
- 50GB disk space
- Python 3.11+

---

## Summary of Risks by Severity

### Critical (Must Handle Before Demo)
1. Ollama not running or model missing
2. Dummy API not started
3. Invalid OpenAPI spec

### Medium (Handle During Demo if Occurs)
4. Network connectivity issues
5. Coverage below threshold
6. AI generation errors (auto-retries)

### Low (Informational Only)
7. Dashboard connection failures (non-critical)
8. Git commit issues (manual fallback)
9. Port conflicts (easily resolved)

---

## Demo Script (5 Minutes)

1. **Show Spec** (30 sec): Open `specs/aadhaar-api.yaml` - explain API
2. **Start Services** (30 sec): Show Ollama, API, Dashboard running
3. **Run Main** (2 min): Execute `python main.py`, watch dashboard
4. **Show Results** (1 min): Open coverage report, show test file
5. **Modify Spec** (1 min): Change spec, run again, show detection
6. **Q&A** (30 sec)

**Total: 5 minutes**
