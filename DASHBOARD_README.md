# Enhanced Dashboard - Complete Integration Guide

## Overview

The dashboard now includes **6 powerful tabs** with real-time monitoring of all API testing features:

1. **Overview** - Original metrics (spec analysis, test generation, execution, coverage)
2. **Self-Healing** - Automatic test repair with AI
3. **Error Analysis** - Deep error breakdown with fix suggestions
4. **API Diff** - Visual comparison of API changes
5. **Anomalies** - ML-based detection of unusual behavior
6. **Traffic Replay** - Production traffic capture and replay

## What's New

### ✅ Updated Files

#### 1. `dashboard/index.html`
- **Added**: Tab navigation bar with 6 tabs
- **Added**: Badge counters for real-time counts
- **Added**: 5 new feature panels (healing, errors, diff, anomalies, traffic)
- **Kept**: All original Overview tab content intact

#### 2. `dashboard/style.css`
- **Added**: ~800 lines of new styles for tabs and features
- **Maintained**: Existing Kyndryl theme and branding
- **Added**: Responsive design for all screen sizes

#### 3. `dashboard/app.js`
- **Added**: Tab switching functionality
- **Added**: 5 new event handlers (healing, error_analysis, api_diff, anomaly, traffic)
- **Added**: Feature state management
- **Added**: UI rendering functions for all new components
- **Kept**: All original event handlers working

#### 4. `dashboard/server.py`
- **No changes needed!** - Already supports all event types through existing infrastructure

## How It Works

### Event Flow

```
Backend Module → dashboard_integration.py → server.py (/api/event) → SSE Stream (/events) → app.js → UI Update
```

### Sending Events from Backend

```python
from dashboard_integration import emit_healing_event

# After healing a test
emit_healing_event(
    test_name='test_auth',
    confidence=0.95,
    old_code=original_code,
    new_code=healed_code
)
```

## Quick Start

### 1. Start the Dashboard

```bash
cd dashboard
python server.py
```

Dashboard opens at: `http://localhost:5050`

### 2. Test Individual Features

```bash
# Test all features independently
python demo_features.py

# Or test specific features
python -c "from demo_features import demo_self_healing; demo_self_healing()"
```

### 3. Integrate with Main Pipeline

Add to `main.py`:

```python
from dashboard_integration import (
    emit_healing_event,
    emit_error_analysis_event,
    emit_api_diff_event,
    emit_anomaly_event,
    emit_traffic_event
)

# In your test execution loop
if test_failed:
    # Try healing
    healing_result = healer.heal_test(test_file, test_name, error)
    if healing_result:
        emit_healing_event(
            test_name=test_name,
            confidence=healing_result['confidence'],
            old_code=healing_result['original_code'],
            new_code=healing_result['healed_code']
        )
    
    # Analyze error
    error_detail = error_analyzer.analyze_failure(failure_data)
    emit_error_analysis_event(
        test_name=test_name,
        error_type=error_detail.error_type,
        message=error_detail.message,
        root_cause=error_detail.root_cause,
        suggestions=error_detail.suggestions
    )
```

## Tab-by-Tab Guide

### 1. Overview Tab (Default)

**Shows:**
- API specification analysis
- Test generation progress
- Test execution results (passed/failed/total)
- Code coverage percentage
- Contract testing stats
- Version control status
- CI/CD pipeline info
- Activity log

**Events:**
- `parse` - API spec parsed
- `generate` - Test generation progress
- `execute` - Test execution results
- `coverage` - Coverage analysis
- `contract` - Contract testing
- `git` - Version control
- `cicd` - CI/CD pipeline

### 2. Self-Healing Tab

**Shows:**
- Total healings performed
- Success rate (% with >80% confidence)
- Average confidence score
- List of healing operations with:
  - Test name
  - Confidence bar
  - Timestamp
  - Status (Applied/Needs Review)
- Code diff viewer (click any healing to view)

**Events:**
- `healing` - When a test is auto-repaired

**Event Format:**
```json
{
  "type": "healing",
  "test_name": "test_auth_endpoint",
  "confidence": 0.95,
  "old_code": "...",
  "new_code": "...",
  "diff": {
    "before": "...",
    "after": "..."
  },
  "timestamp": 1698445123
}
```

### 3. Error Analysis Tab

**Shows:**
- Total errors detected
- Unique error types
- Error list with:
  - Error icon
  - Test name
  - Error type and message
  - Root cause
  - Timestamp
- Error details viewer (click any error)
  - Full error details
  - Request/response data
  - Fix suggestions with 💡 icon

**Events:**
- `error_analysis` - When an error is analyzed

**Event Format:**
```json
{
  "type": "error_analysis",
  "test_name": "test_payment",
  "error_type": "AssertionError",
  "message": "Expected 200, got 401",
  "root_cause": "Missing auth header",
  "suggestions": [
    "Add Authorization header",
    "Check API key validity"
  ],
  "request": {
    "method": "POST",
    "url": "...",
    "headers": {}
  },
  "response": {
    "status_code": 401,
    "body": {}
  },
  "timestamp": 1698445123
}
```

### 4. API Diff Tab

**Shows:**
- Breaking changes count (red)
- Non-breaking changes count (green)
- Total changes
- Change list with:
  - Change type badge (Added/Removed/Modified)
  - Affected path
  - Description
  - Recommendation box (blue)

**Events:**
- `api_diff` - When specs are compared

**Event Format:**
```json
{
  "type": "api_diff",
  "changes": [
    {
      "type": "removed",
      "path": "/api/v1/deprecated",
      "description": "Endpoint removed",
      "breaking": true,
      "recommendation": "Migrate to v2"
    }
  ]
}
```

### 5. Anomalies Tab

**Shows:**
- Anomaly list with:
  - Severity badge (Critical/High/Medium)
  - Endpoint name
  - Description
  - Expected vs Actual values
  - Timestamp
- Color-coded by severity:
  - Red: Critical
  - Orange: High
  - Blue: Medium

**Events:**
- `anomaly` - When anomaly is detected

**Event Format:**
```json
{
  "type": "anomaly",
  "endpoint": "/api/users",
  "severity": "high",
  "type": "response_time",
  "description": "Response time 3x baseline",
  "expected": "100ms",
  "actual": "350ms",
  "timestamp": 1698445123
}
```

### 6. Traffic Replay Tab

**Shows:**
- Recording/Replay control buttons
- Traffic list (last 100 requests) with:
  - HTTP method badge (color-coded)
  - URL
  - Status code (green=success, red=error)
  - Timestamp

**Events:**
- `traffic` - When traffic is recorded

**Event Format:**
```json
{
  "type": "traffic",
  "method": "POST",
  "url": "https://api.example.com/orders",
  "status_code": 201,
  "response_time": 45.2,
  "timestamp": 1698445123
}
```

## UI Features

### Real-Time Updates
- **SSE (Server-Sent Events)**: No polling, instant updates
- **Auto-reconnect**: Handles connection loss gracefully
- **Badge counters**: Live counts on each tab
- **Smooth animations**: Fade-in effects for new items

### Interactive Elements
- **Click items**: View detailed information
- **Code diffs**: Side-by-side comparison
- **Error details**: Full request/response
- **Scrollable lists**: Max heights with custom scrollbars

### Visual Design
- **Kyndryl branding**: Maintained red/black theme
- **Color coding**:
  - Red: Errors, breaking changes, critical
  - Green: Success, non-breaking, passed
  - Orange: Warnings, high severity
  - Blue: Info, recommendations
- **Responsive**: Works on desktop, tablet, mobile

### Empty States
- Helpful messages when no data:
  - "No healing operations yet"
  - "No errors detected"
  - "No API changes detected"
  - "No anomalies detected"
  - "No traffic recorded"

## Testing the Dashboard

### Manual Test

1. **Start dashboard**:
```bash
python dashboard/server.py
```

2. **Open browser**: `http://localhost:5050`

3. **Send test events** (in another terminal):
```bash
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "healing",
    "test_name": "test_example",
    "confidence": 0.95,
    "old_code": "assert False",
    "new_code": "assert True",
    "diff": {
      "before": "assert False",
      "after": "assert True"
    }
  }'
```

4. **Check UI**: Switch to Self-Healing tab, see the new item

### Automated Test

```bash
# Run the demo script
python demo_features.py

# Watch events appear in dashboard
```

## Integration Checklist

- [ ] Dashboard running on `http://localhost:5050`
- [ ] All 6 tabs visible and switchable
- [ ] Original Overview tab working (spec, tests, coverage)
- [ ] New tabs show empty states
- [ ] Send test healing event - appears in Self-Healing tab
- [ ] Send test error event - appears in Error Analysis tab
- [ ] Send test diff event - appears in API Diff tab
- [ ] Send test anomaly event - appears in Anomalies tab
- [ ] Send test traffic event - appears in Traffic Replay tab
- [ ] Badge counters updating
- [ ] Click items to view details
- [ ] Activity log showing all events
- [ ] No console errors

## File Structure

```
aadhaar-api-test-poc/
├── dashboard/
│   ├── server.py              # ✅ No changes needed
│   ├── index.html             # ✅ Updated with tabs
│   ├── style.css              # ✅ Updated with new styles
│   └── app.js                 # ✅ Updated with new handlers
├── dashboard_integration.py   # ✅ New - helper functions
├── src/
│   ├── self_healing.py       # ✅ Backend ready
│   ├── error_analyzer.py     # ✅ Backend ready
│   ├── api_diff.py           # ✅ Backend ready
│   ├── anomaly_detector.py   # ✅ Backend ready
│   └── traffic_replay.py     # ✅ Backend ready
└── main.py                    # ⏳ Needs integration
```

## Next Steps

1. **Import helper functions** in `main.py`:
```python
from dashboard_integration import (
    emit_healing_event,
    emit_error_analysis_event,
    emit_api_diff_event,
    emit_anomaly_event,
    emit_traffic_event
)
```

2. **Call emit functions** after each operation:
   - After healing → `emit_healing_event(...)`
   - After error analysis → `emit_error_analysis_event(...)`
   - After diff detection → `emit_api_diff_event(...)`
   - After anomaly detection → `emit_anomaly_event(...)`
   - When recording traffic → `emit_traffic_event(...)`

3. **Test end-to-end**:
   - Run full pipeline: `python main.py --spec examples/api.yaml --dashboard`
   - Watch dashboard update in real-time
   - Switch between tabs to see different features

## Troubleshooting

### Dashboard Not Updating

**Check:**
- Dashboard server running on port 5050
- Browser console for SSE connection errors
- Network tab shows `/events` stream connected

**Fix:**
```bash
# Restart dashboard
pkill -f "server.py"
python dashboard/server.py
```

### Events Not Appearing

**Check:**
- Event format matches expected structure
- Event type spelled correctly (case-sensitive)
- `requests` library installed: `pip install requests`

**Test:**
```bash
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{"type":"healing","test_name":"test"}'
```

### Tab Not Switching

**Check:**
- Browser console for JavaScript errors
- `app.js` loaded correctly
- Tab buttons have `data-tab` attribute

**Fix:**
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Clear cache

### Styles Look Broken

**Check:**
- `style.css` loaded (Network tab)
- No CSS syntax errors

**Fix:**
```bash
# Verify file exists
ls -la dashboard/style.css

# Check for syntax errors
# (look for unclosed brackets)
```

## Performance

- **SSE connection**: Lightweight, ~1KB/min
- **Badge updates**: O(1) operation
- **List rendering**: Optimized with DocumentFragment
- **Memory**: Auto-cleanup (max 100 traffic items, 50 log entries)
- **Animations**: GPU-accelerated CSS transforms

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Opera 76+

**Requires:**
- JavaScript enabled
- EventSource API (all modern browsers)
- CSS Grid support

## Security Notes

- **CORS enabled**: For local development
- **No authentication**: Dashboard is open (add auth for production)
- **Input sanitization**: HTML escaped in UI
- **XSS prevention**: No `innerHTML` with user input

## Demo Tips

**For impressive demo:**

1. **Start with Overview**: Show existing functionality
2. **Break a test**: Manually modify to fail
3. **Watch Self-Healing**: See it auto-fix
4. **Click healing item**: Show code diff
5. **Switch to Errors**: See detailed analysis
6. **Click error**: Show fix suggestions
7. **Compare specs**: Upload modified spec
8. **View API Diff**: See breaking vs non-breaking
9. **Run load test**: Trigger anomalies
10. **Record traffic**: Show capture and replay

**Talking points:**
- "Real-time updates, no refresh needed"
- "AI-powered self-healing with confidence scores"
- "Actionable error analysis with fix suggestions"
- "Visual API diff shows exactly what changed"
- "ML detects anomalies before they become problems"
- "Production traffic becomes tests automatically"

## Summary

✅ **All existing functionality preserved**
✅ **6 tabs with rich features**
✅ **Real-time SSE updates**
✅ **Kyndryl branding maintained**
✅ **Responsive design**
✅ **Ready for demo**

The dashboard is now a **comprehensive monitoring solution** for your API testing platform!
