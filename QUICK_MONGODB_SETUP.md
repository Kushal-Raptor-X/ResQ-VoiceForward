# Quick MongoDB Setup Guide

## 1. Install Motor Package

```bash
cd backend
pip install motor
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## 2. Verify MongoDB Connection

Your MongoDB URI is already configured in `backend/.env`:
```
MONGO_URI=mongodb+srv://puneetsdhongade2006_db_user:SDVQY6ba7CtDCxqR@cluster0.vqv0vyn.mongodb.net/?appName=Cluster0
```

## 3. Test the Integration

```bash
cd backend
python test_mongodb_integration.py
```

Expected output:
```
=== Testing MongoDB Integration ===

1. Testing MongoDB connection...
   ✓ Connected to MongoDB Atlas
   Connection status: True

2. Testing call logging...
   ✓ Call logged successfully (ID: ...)

3. Testing call retrieval...
   ✓ Total calls in database: X
   ✓ Retrieved test call:
     - Session ID: test_session_123
     - Risk Level: MEDIUM
     - Risk Score: 45
     - Confidence: HIGH

4. Cleaning up test data...
   ✓ Deleted 1 test records

=== Test Complete ===
```

## 4. Start the System

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

Look for:
```
[db] ✓ Connected to MongoDB Atlas — 'voiceforward' (X existing records)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 5. Test in UI

1. Open http://localhost:5173
2. Click "Start Call Transcript"
3. Wait for AI analysis to run (you'll see updates in real-time)
4. Click "Call History" tab in navbar
5. You should see your call logs with:
   - Session ID and timestamp
   - Risk level (color-coded)
   - Confidence level
   - Triggered signals
   - Operator action
   - Transcript preview
6. Test delete functionality:
   - Click "Delete" on individual calls
   - Click "Delete All" to clear all logs (requires double confirmation)

## 6. Verify MongoDB Storage

Check the storage indicator in Call History view:
- Should show: "Call History (MongoDB Atlas)"
- If offline: "Call History (in-memory)"

## API Endpoints Available

- `GET /calls` - Fetch all call logs
- `GET /calls/{call_id}` - Get specific call details
- `DELETE /calls/{call_id}` - Delete specific call
- `DELETE /calls` - Delete all calls
- `POST /calls/{call_id}/action` - Update operator action
- `GET /health` - Check MongoDB status
- `GET /db-status` - Detailed connection info

## Troubleshooting

### Motor not installed
```bash
pip install motor
```

### MongoDB connection fails
- Check internet connection
- Verify MongoDB URI in `backend/.env`
- System will automatically fall back to in-memory storage

### No calls showing in UI
- Make sure backend is running
- Start a call and wait for analysis
- Check browser console for errors
- Verify backend logs for MongoDB connection status

## What Gets Stored (Layer 4 & 5)

Every call analysis automatically logs:
- **Layer 4 (Learning):**
  - Full transcript (privacy-filtered)
  - Risk level and score
  - Agent verdicts
  - Triggered signals
  - Operator actions and outcomes
  
- **Layer 5 (Audit):**
  - Privacy redactions applied
  - STT confidence scores
  - AI reasoning transparency
  - Resource recommendations
  - Timestamps for audit trail

## Status Check

Run this to check everything:
```bash
cd backend
python -c "import motor; print('✓ Motor installed')"
python test_mongodb_integration.py
```

If both succeed, you're ready to demo! 🚀
