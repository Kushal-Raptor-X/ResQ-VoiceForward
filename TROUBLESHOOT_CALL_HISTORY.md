# Troubleshooting Call History

## Problem: "No call logs found" in Call History tab

### Step 1: Verify MongoDB has data

```bash
cd backend
python debug_call_history.py
```

**Expected output:**
```
✅ Found X call(s) in database
```

**If you see "❌ No calls found":**
- You need to create a call first
- Go to Step 5 below

**If you see "✅ Found X calls":**
- Data exists in MongoDB
- Continue to Step 2

---

### Step 2: Verify backend is running

**Check Terminal 1 (backend):**
Should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If not running:**
```bash
cd backend
python main.py
```

**If port 8000 is in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Then restart
python main.py
```

---

### Step 3: Test REST API directly

**While backend is running, open in browser:**

http://localhost:8000/calls

**Expected response:**
```json
{
  "calls": [...],
  "total": 1,
  "storage": "MongoDB Atlas"
}
```

**If you see this:**
- Backend API is working ✅
- Continue to Step 4

**If you see error or can't connect:**
- Backend isn't running
- Go back to Step 2

---

### Step 4: Check frontend console

1. Open http://localhost:5173
2. Press F12 to open DevTools
3. Go to "Console" tab
4. Click "Call History" tab in app
5. Look for messages starting with `[CallHistory]`

**Expected console output:**
```
[CallHistory] Fetching calls from backend...
[CallHistory] Response status: 200
[CallHistory] Received data: {calls: Array(1), total: 1, storage: "MongoDB Atlas"}
[CallHistory] Loaded 1 calls from MongoDB Atlas
```

**If you see CORS error:**
```
Access to fetch at 'http://localhost:8000/calls' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Fix:** Check `backend/main.py` has correct CORS origins:
```python
ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
```

**If you see "Failed to fetch":**
- Backend isn't running
- Go back to Step 2

**If you see "HTTP 500" error:**
- Check backend terminal for error logs
- There might be a bug in the API

---

### Step 5: Create a test call

If database is empty, create a call:

1. Make sure backend is running
2. Open http://localhost:5173
3. Click "Start Call Transcript" button
4. Wait 10 seconds
5. Check backend logs for:
   ```
   ✓ AI analysis complete in X.XXs - Risk: MEDIUM (55/100)
   ✓ Logged to database: <some_id>
   ```
6. Go to "Call History" tab
7. Click "Refresh" button

**If still not showing:**
- Check backend logs for errors
- Run: `cd backend && python debug_call_history.py`
- Check if call was actually logged

---

### Step 6: Check Network tab

1. Open http://localhost:5173
2. Press F12 → "Network" tab
3. Click "Call History" tab in app
4. Look for request to `calls?limit=50`

**Click on the request and check:**

**Headers tab:**
- Request URL: http://localhost:8000/calls?limit=50
- Status Code: 200 OK

**Response tab:**
Should show JSON with calls array

**If Status Code is 404:**
- Backend route not registered
- Check `backend/main.py` has `@fastapi_app.get("/calls")`

**If Status Code is 500:**
- Server error
- Check backend terminal for error logs

---

## Quick Fixes

### Fix 1: Restart everything
```bash
# Stop backend (Ctrl+C in Terminal 1)
# Stop frontend (Ctrl+C in Terminal 2)

# Terminal 1
cd backend
python main.py

# Terminal 2
cd frontend
npm run dev
```

### Fix 2: Clear browser cache
1. Press Ctrl+Shift+Delete
2. Clear "Cached images and files"
3. Refresh page (Ctrl+F5)

### Fix 3: Use different browser
- Try Chrome, Firefox, or Edge
- Sometimes browser extensions block requests

### Fix 4: Check firewall
- Windows Firewall might block localhost:8000
- Temporarily disable to test

### Fix 5: Reinstall dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm install
```

---

## Still Not Working?

### Run full diagnostic:

```bash
# Terminal 1
cd backend
python debug_call_history.py

# Terminal 2 (keep Terminal 1 open)
cd backend
python main.py

# Terminal 3 (new window)
cd backend
python test_rest_api.py
```

**All 3 should succeed.**

### Check these files:

1. **backend/.env** - Should have:
   ```
   MONGO_URI=mongodb+srv://puneetsdhongade2006_db_user:SDVQY6ba7CtDCxqR@cluster0.vqv0vyn.mongodb.net/?appName=Cluster0
   ```

2. **backend/main.py** - Should have:
   ```python
   ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
   
   @fastapi_app.get("/calls")
   async def get_calls(limit: int = 50, skip: int = 0):
       # ... code ...
   ```

3. **frontend/src/components/CallHistoryView.jsx** - Should have:
   ```javascript
   const response = await fetch("http://localhost:8000/calls?limit=50");
   ```

---

## Success Checklist

- [ ] MongoDB has data (run `debug_call_history.py`)
- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 5173
- [ ] http://localhost:8000/calls returns JSON
- [ ] Browser console shows `[CallHistory] Loaded X calls`
- [ ] Call History tab shows call cards

**If all checked, it should work!** ✅

---

## Common Mistakes

1. **Backend not running** - Most common issue
2. **Wrong port** - Backend must be on 8000, frontend on 5173
3. **CORS not configured** - Check ALLOWED_ORIGINS
4. **No data in database** - Create a call first
5. **Browser cache** - Clear cache and hard refresh

---

## Get Help

If still stuck, provide:
1. Output of `python debug_call_history.py`
2. Backend terminal logs
3. Browser console logs (F12)
4. Network tab screenshot showing the /calls request

This will help diagnose the exact issue!
