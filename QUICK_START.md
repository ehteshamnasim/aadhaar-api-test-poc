# 🚀 QUICK START - Get Dashboard Working NOW

## The Problem
You're seeing data in the **Overview tab** but **other tabs are empty** (Self-Healing, Error Analysis, API Diff, Anomalies, Traffic Replay).

## The Solution (3 Minutes)

### Step 1: Install Packages (30 seconds)
```bash
pip3 install flask flask-cors requests
```

### Step 2: Start Dashboard (10 seconds)
```bash
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python3 dashboard/server.py
```
**Keep this terminal open!**

### Step 3: Send Test Data (10 seconds)
**Open NEW terminal:**
```bash
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python3 test_dashboard.py
```

### Step 4: Check Browser (30 seconds)
1. Open: `http://localhost:5050`
2. Click each tab
3. See data in all tabs!

---

## ✅ What You Should See

| Tab | What Appears | Badge Count |
|-----|-------------|-------------|
| **Overview** | Original metrics | - |
| **Self-Healing** | 3 healing operations | 3 |
| **Error Analysis** | 3 error breakdowns | 3 |
| **API Diff** | 5 API changes | 5 |
| **Anomalies** | 4 anomalies detected | 4 |
| **Traffic Replay** | 10 recorded requests | 10 |

---

## 🐛 If It Doesn't Work

### Quick Diagnostic Test
```bash
python3 quick_test.py
```

**If it passes:** Problem is in browser (try Cmd+Shift+R to refresh)  
**If it fails:** Problem is with dashboard server

### Check Browser Console
1. Press **F12**
2. Click **Console** tab
3. Look for **red errors**

Common errors:
- `featureState is not defined` → Hard refresh (Cmd+Shift+R)
- `Cannot connect to SSE` → Dashboard server not running
- `404 Not Found` → Wrong port (should be 5050)

### Manual Test (If Nothing Works)
```bash
# Terminal 1: Make sure dashboard is running
python3 dashboard/server.py

# Terminal 2: Send ONE healing event manually
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{"type":"healing","test_name":"test_fix","confidence":0.95,"old_code":"old","new_code":"new","diff":{"before":"old","after":"new"}}'

# Browser: Refresh and check Self-Healing tab
```

---

## 📚 More Help

- **Detailed troubleshooting:** Read `TROUBLESHOOTING.md`
- **Step-by-step guide:** Read `FIX_STEPS.md`
- **Test scenarios:** Read `SIMPLE_TEST_SCENARIOS.md`

---

## 💡 Quick Tips

1. **Always keep dashboard running** in Terminal 1
2. **Use Terminal 2** for test commands
3. **Hard refresh browser** after sending events (Cmd+Shift+R)
4. **Check browser console (F12)** if tabs are empty
5. **Look at Terminal 1** for server errors

---

## ✅ Verification Command

Run this to test everything:

```bash
# Test dashboard health
curl http://localhost:5050/api/health

# Should return: {"status":"healthy"}
```

If this works, dashboard is running correctly. If not, restart dashboard server.

---

## 🎯 Expected Flow

```
Terminal 1: Dashboard Server Running
     ↓
Terminal 2: Send Events (test_dashboard.py)
     ↓
Dashboard Server: Receives events via POST /api/event
     ↓
Dashboard Server: Broadcasts via SSE (Server-Sent Events)
     ↓
Browser: Receives SSE messages
     ↓
app.js: Handles events (handleHealingEvent, etc.)
     ↓
Tabs: Display data
```

If any step breaks, check that specific component.

---

## 🚨 Emergency Commands

```bash
# Stop all Python processes
pkill -f python

# Check if port 5050 is free
lsof -i :5050

# Force kill if needed
lsof -ti :5050 | xargs kill -9

# Start fresh
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python3 dashboard/server.py
```

---

## ✨ Success!

When it works, you'll see:
- All 6 tabs have content
- Badge counters show numbers
- Clicking items shows details
- Browser console has no errors

**Now you can integrate with your actual API!** 🎉
