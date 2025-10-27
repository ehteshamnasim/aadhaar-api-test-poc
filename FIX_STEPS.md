# STEP-BY-STEP: Fix Dashboard Empty Tabs

Follow these steps **EXACTLY** to get all tabs working:

---

## 🎯 Step 1: Install Required Python Packages

```bash
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
pip3 install flask flask-cors requests
```

**Wait for installation to complete.**

---

## 🎯 Step 2: Start Dashboard Server

```bash
# Open Terminal 1
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python3 dashboard/server.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5050
 * Running on http://0.0.0.0:5050
```

**Keep this terminal open!** Don't close it.

---

## 🎯 Step 3: Test Dashboard Connection

```bash
# Open Terminal 2 (NEW terminal)
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python3 quick_test.py
```

**Expected Output:**
```
✅ Dashboard is running!
✅ Event sent successfully!
```

**If it says "Cannot connect":**
- Go back to Terminal 1
- Make sure server is running
- Check for any error messages

---

## 🎯 Step 4: Open Browser

1. **Open Chrome or Firefox**
2. **Go to:** `http://localhost:5050`
3. **You should see the dashboard with 6 tabs:**
   - Overview
   - Self-Healing
   - Error Analysis
   - API Diff
   - Anomalies
   - Traffic Replay

---

## 🎯 Step 5: Send Test Events

```bash
# In Terminal 2 (keep Terminal 1 running!)
python3 test_dashboard.py
```

**Expected Output:**
```
📋 Testing Self-Healing Events...
✅ Sent healing event
✅ Sent healing event
✅ Sent healing event

📋 Testing Error Analysis Events...
✅ Sent error_analysis event
✅ Sent error_analysis event
✅ Sent error_analysis event

...and so on
```

---

## 🎯 Step 6: Check Browser

**In the browser (http://localhost:5050):**

1. **Click "Self-Healing" tab**
   - Should see 3 healing operations
   - Badge should show "3"

2. **Click "Error Analysis" tab**
   - Should see 3 errors
   - Badge should show "3"

3. **Click "API Diff" tab**
   - Should see 5 changes
   - 2 breaking (red), 3 non-breaking (green)

4. **Click "Anomalies" tab**
   - Should see 4 anomalies
   - Different severity colors

5. **Click "Traffic Replay" tab**
   - Should see 10 requests
   - Different HTTP methods (GET, POST, etc.)

---

## 🐛 If Tabs Are Still Empty:

### Check 1: Browser Console

1. **Press F12** (or Right-click → Inspect)
2. **Click "Console" tab**
3. **Look for red errors**

**If you see errors:**
- Take a screenshot
- Share the error messages

### Check 2: Server Terminal

**Look at Terminal 1 (running dashboard/server.py)**

**You should see:**
```
Broadcasting event: healing
Broadcasting event: error_analysis
Broadcasting event: api_diff
Broadcasting event: anomaly
Broadcasting event: traffic
```

**If you DON'T see these:**
- Events aren't reaching the server
- Server might have crashed
- Check for Python errors in Terminal 1

### Check 3: Hard Refresh Browser

```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

This clears the cache and reloads everything.

---

## 🔧 Still Not Working? Try This:

### Option A: Use curl to test manually

```bash
# Send a healing event
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{"type":"healing","test_name":"manual_test","confidence":0.95,"old_code":"old","new_code":"new","diff":{"before":"old","after":"new"}}'
```

**Expected:** Returns `{"status":"ok"}`

**Then:** Refresh browser, click Self-Healing tab, should see "manual_test"

### Option B: Check if SSE is working

**In browser console (F12), type:**
```javascript
console.log('SSE Active:', window.eventSource !== null);
```

**Should print:** `SSE Active: true`

**If false:** SSE connection failed. Check Terminal 1 for errors.

---

## ✅ Success Checklist

After following all steps, you should have:

- [x] Terminal 1: Dashboard server running without errors
- [x] Terminal 2: test_dashboard.py completed successfully
- [x] Browser: Dashboard open at http://localhost:5050
- [x] Browser Console (F12): No red JavaScript errors
- [x] Self-Healing tab: 3 items visible
- [x] Error Analysis tab: 3 items visible
- [x] API Diff tab: 5 items visible
- [x] Anomalies tab: 4 items visible
- [x] Traffic Replay tab: 10 items visible
- [x] Badge counters: All show numbers > 0

---

## 📸 What You Should See

### Self-Healing Tab:
```
╔═══════════════════════════════════════════╗
║ Self-Healing Tracker                       ║
╠═══════════════════════════════════════════╣
║ [Total: 3] [Success: 100%] [Conf: 85%]   ║
╠═══════════════════════════════════════════╣
║ ✓ test_authentication_endpoint    [95%]   ║
║ ✓ test_payment_api                [88%]   ║
║ ✓ test_user_registration          [72%]   ║
╚═══════════════════════════════════════════╝
```

### Error Analysis Tab:
```
╔═══════════════════════════════════════════╗
║ Error Analysis                             ║
╠═══════════════════════════════════════════╣
║ [Total: 3] [Critical: 1] [High: 2]       ║
╠═══════════════════════════════════════════╣
║ ⚠ test_payment_api - AssertionError      ║
║ ⚠ test_user_login - HTTPError             ║
║ ⚠ test_data_validation - ValueError       ║
╚═══════════════════════════════════════════╝
```

---

## 🚨 Emergency Reset

If NOTHING works:

```bash
# 1. Stop everything
pkill -f "python.*dashboard/server.py"

# 2. Reinstall packages
pip3 install --force-reinstall flask flask-cors requests

# 3. Start fresh
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python3 dashboard/server.py

# 4. In NEW terminal:
python3 quick_test.py

# 5. Open NEW incognito browser window:
# Chrome: Cmd+Shift+N
# Firefox: Cmd+Shift+P

# 6. Go to: http://localhost:5050

# 7. Send events:
python3 test_dashboard.py
```

---

## 💡 Common Mistakes

### Mistake 1: Wrong Terminal
- Make sure Terminal 1 stays open with dashboard server running
- Use Terminal 2 for test scripts

### Mistake 2: Wrong Port
- Dashboard runs on **port 5050**, not 5000 or 5001
- API runs on **port 5001**

### Mistake 3: Not Waiting
- Wait 2-3 seconds after sending events
- Then refresh browser

### Mistake 4: Old Browser Cache
- Always do hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Win)

---

## 📞 Need More Help?

Run the diagnostic:

```bash
cd /Users/ehtesham/Developer/aadhaar-api-test-poc

echo "Checking files..."
ls -la dashboard/server.py dashboard/app.js dashboard/index.html

echo "Checking if port 5050 is in use..."
lsof -i :5050

echo "Testing connection..."
curl http://localhost:5050/api/health

echo "Done!"
```

Send me the output of this command.
