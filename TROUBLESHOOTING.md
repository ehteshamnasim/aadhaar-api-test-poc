# Troubleshooting Guide - Dashboard Not Showing Data

## 🔴 Problem: Only Overview Tab Shows Data

If you're seeing data in the Overview tab but NOT in Self-Healing, Error Analysis, API Diff, Anomalies, or Traffic Replay tabs, follow these steps:

---

## ✅ Step 1: Verify Dashboard is Running

```bash
# Terminal 1: Start dashboard
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python3 dashboard/server.py
```

You should see:
```
 * Running on http://0.0.0.0:5050
```

**If you see "ModuleNotFoundError: No module named 'flask'":**
```bash
pip3 install flask flask-cors requests
```

---

## ✅ Step 2: Test Dashboard Connection

```bash
# Terminal 2: Run quick test
python3 quick_test.py
```

**Expected output:**
```
✅ Dashboard is running!
✅ Event sent successfully!
```

**If it fails:** Dashboard is not running or there's a connection issue.

---

## ✅ Step 3: Send Test Events

```bash
# Terminal 2: Send sample events to all tabs
python3 test_dashboard.py
```

**Expected output:**
```
✅ Sent healing event
✅ Sent error_analysis event
✅ Sent api_diff event
✅ Sent anomaly event
✅ Sent traffic event
```

---

## ✅ Step 4: Check Browser

1. **Open:** http://localhost:5050
2. **Open Browser Console:** Press F12
3. **Look for errors in console**

### Common Browser Errors:

**Error: "Uncaught ReferenceError: featureState is not defined"**
- **Cause:** app.js didn't load properly or has syntax errors
- **Fix:** Check dashboard/app.js line 1-50 for `featureState` initialization

**Error: "Cannot read property 'push' of undefined"**
- **Cause:** featureState arrays not initialized
- **Fix:** Verify featureState object exists at top of app.js

**No errors but tabs empty:**
- **Cause:** Event handlers not connected to SSE
- **Fix:** Check app.js lines 430-450 for case statements

---

## ✅ Step 5: Check Server Logs

In the terminal running `dashboard/server.py`, you should see:

```
Broadcasting event: healing
Broadcasting event: error_analysis
Broadcasting event: api_diff
Broadcasting event: anomaly
Broadcasting event: traffic
```

**If you DON'T see these:**
- Events are not reaching the server
- Check if DASHBOARD_URL in test scripts is correct (http://localhost:5050)

---

## 🔧 Quick Fix: Manual Test via curl

Test each tab individually:

### Test Self-Healing Tab:
```bash
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "healing",
    "test_name": "test_manual",
    "confidence": 0.95,
    "old_code": "assert x == 1",
    "new_code": "assert x == 2",
    "diff": {"before": "assert x == 1", "after": "assert x == 2"}
  }'
```

**Then:** Refresh browser, click "Self-Healing" tab, should see "test_manual"

### Test Error Analysis Tab:
```bash
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "error_analysis",
    "test_name": "test_error",
    "error_type": "AssertionError",
    "message": "Test failed",
    "root_cause": "Wrong value",
    "suggestions": ["Fix it"],
    "request": {"method": "GET"},
    "response": {"status_code": 500}
  }'
```

### Test API Diff Tab:
```bash
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "api_diff",
    "changes": [{
      "type": "modified",
      "path": "/test",
      "description": "Changed",
      "breaking": true,
      "recommendation": "Update tests"
    }]
  }'
```

### Test Anomalies Tab:
```bash
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "anomaly",
    "endpoint": "/api/test",
    "severity": "critical",
    "anomaly_type": "response_time",
    "description": "Too slow",
    "expected": "100ms",
    "actual": "500ms"
  }'
```

### Test Traffic Replay Tab:
```bash
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "traffic",
    "method": "POST",
    "url": "http://test.com/api",
    "status_code": 200
  }'
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "Nothing appears in tabs"

**Check 1:** Browser console for JavaScript errors
```
F12 → Console tab → Look for red errors
```

**Check 2:** SSE connection status
```javascript
// In browser console, type:
console.log('SSE connection active:', window.eventSource);
```

**Check 3:** Event handler functions exist
```javascript
// In browser console, type:
console.log(typeof handleHealingEvent);
// Should print: "function"
```

### Issue 2: "Events sent but don't appear"

**Cause:** SSE not broadcasting properly

**Fix:** Check dashboard/server.py for this code:
```python
@app.route('/api/event', methods=['POST'])
def handle_event():
    data = request.get_json()
    broadcast_event(data)  # ← This line MUST be here
    return jsonify({'status': 'ok'})
```

### Issue 3: "Only old events appear"

**Cause:** Browser cached old SSE stream

**Fix:** Hard refresh browser
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

### Issue 4: "Badge counts don't update"

**Cause:** Badge update code not running

**Fix:** Check app.js for badge updates:
```javascript
const badge = document.getElementById('healing-badge');
if (badge) badge.textContent = featureState.healings.length;
```

---

## 🔍 Debug Mode

Add debug logging to app.js:

```javascript
// Add at top of handleHealingEvent function (line ~763)
function handleHealingEvent(data) {
    console.log('🔧 DEBUG: Healing event received:', data);  // ADD THIS
    featureState.healings.push(data);
    // ... rest of code
}
```

Do the same for all handler functions, then check browser console.

---

## ✅ Verification Checklist

Run through this checklist:

- [ ] Dashboard server running on port 5050
- [ ] Browser open at http://localhost:5050
- [ ] Browser console shows no JavaScript errors
- [ ] `python3 quick_test.py` passes all checks
- [ ] `python3 test_dashboard.py` sends events successfully
- [ ] Server terminal shows "Broadcasting event: ..." messages
- [ ] Browser console shows SSE messages arriving
- [ ] Tab buttons are clickable and switch views
- [ ] Badge counters exist in HTML (inspect element)

---

## 🚨 Nuclear Option: Reset Everything

If nothing works, reset completely:

```bash
# 1. Stop all running processes
pkill -f "dashboard/server.py"
pkill -f "api/dummy_aadhaar_api.py"

# 2. Clear browser cache
# In browser: Settings → Privacy → Clear browsing data

# 3. Restart dashboard
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python3 dashboard/server.py

# 4. Open NEW incognito window
# Cmd+Shift+N (Chrome) or Cmd+Shift+P (Firefox)

# 5. Go to http://localhost:5050

# 6. Send test event
python3 quick_test.py

# 7. Check Self-Healing tab
```

---

## 📧 Still Not Working?

Check these files are correct:

1. **dashboard/index.html** - Has all 6 tabs defined
2. **dashboard/app.js** - Has featureState and all handlers
3. **dashboard/server.py** - Has broadcast_event function
4. **dashboard/style.css** - Has .tab-pane styles

Run this check:
```bash
grep -n "healing-tab" dashboard/index.html
grep -n "function handleHealingEvent" dashboard/app.js
grep -n "def broadcast_event" dashboard/server.py
grep -n ".tab-pane" dashboard/style.css
```

All should return results. If any returns nothing, that file needs to be updated.

---

## 🎯 Quick Test Command

Run this all-in-one test:

```bash
# Test everything in sequence
python3 quick_test.py && \
echo "Waiting 2 seconds..." && sleep 2 && \
python3 test_dashboard.py && \
echo "" && \
echo "✅ All tests complete! Check http://localhost:5050"
```

---

## 📊 Expected Behavior

After running `python3 test_dashboard.py`, you should see:

**Self-Healing Tab:** 3 items with confidence scores  
**Error Analysis Tab:** 3 errors with suggestions  
**API Diff Tab:** 5 changes (2 breaking, 3 non-breaking)  
**Anomalies Tab:** 4 anomalies (critical, high, medium)  
**Traffic Replay Tab:** 10 recorded requests  
**Overview Tab:** Activity log with all events  

If you see this, everything is working! ✅
