# Start ResQ VoiceForward System

## Quick Start (2 Terminals)

### Terminal 1: Backend
```bash
cd backend
python main.py
```

**Expected output:**
```
[db] Connecting to MongoDB Atlas (db='voiceforward')...
[db] ✓ Connected to MongoDB Atlas — 'voiceforward' (X existing records)
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**If you see this, backend is ready! ✅**

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

**If you see this, frontend is ready! ✅**

## Open Browser

Go to: **http://localhost:5173**

## Test Call History

1. Click "Call History" tab in navbar
2. You should see existing calls from database
3. If empty, click "Start Call Transcript" first to create a call
4. Wait 10 seconds for analysis
5. Go back to "Call History" tab

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed (Windows)
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

### Frontend won't start
```bash
# Check if port 5173 is in use
netstat -ano | findstr :5173

# Kill process if needed
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 5174
```

### Call History shows "Loading..."
- Check backend is running (Terminal 1 should show logs)
- Check browser console (F12) for errors
- Check Network tab for failed requests to http://localhost:8000/calls
- Try clicking "Refresh" button

### Call History shows "Error: ..."
- Check backend logs for errors
- Verify MongoDB connection in backend logs
- Try: `cd backend && python debug_call_history.py`

### No calls appearing after starting call
- Wait at least 10 seconds for first analysis
- Check backend logs for: "✓ Logged to database: ..."
- If not logging, check: `cd backend && python test_call_logging.py`

## Verify Everything Works

Run this in backend directory:
```bash
python debug_call_history.py
```

Should show:
```
✅ Found X call(s) in database
```

## Quick Health Check

While backend is running, open in browser:
- http://localhost:8000/health
- http://localhost:8000/db-status
- http://localhost:8000/calls

All should return JSON responses.

## Demo Mode

If you want to use demo audio instead of microphone:

1. Edit `backend/.env`:
   ```
   AUDIO_SOURCE=demo
   ```

2. Restart backend

3. Start call in UI

4. Demo audio will play automatically

## Full System Check

```bash
# Terminal 1
cd backend
python main.py

# Terminal 2 (new window)
cd backend
python test_rest_api.py

# Terminal 3 (new window)
cd frontend
npm run dev
```

If all 3 succeed, system is fully operational! 🚀
