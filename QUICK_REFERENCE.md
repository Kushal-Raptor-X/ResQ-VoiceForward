# ResQ VoiceForward - Quick Reference

## 🚀 Start System (2 Commands)

```bash
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

**Open:** http://localhost:5173

---

## ✅ Verify Everything Works

```bash
cd backend
python debug_call_history.py
```

**Expected:** `✅ Found X call(s) in database`

---

## 🔍 Test Call History

1. Open http://localhost:5173
2. Click "Call History" tab
3. Should see existing calls
4. Click "Refresh" to reload

---

## 📝 Create New Call

1. Click "Start Call Transcript"
2. Wait 10 seconds
3. Backend logs: `✓ Logged to database: ...`
4. Go to "Call History" tab
5. New call appears

---

## 🐛 Troubleshooting

### No calls showing?

**Quick fix:**
```bash
# Check database
cd backend
python debug_call_history.py

# Restart backend
python main.py
```

**Detailed fix:** See `TROUBLESHOOT_CALL_HISTORY.md`

### Backend won't start?

```bash
# Install dependencies
pip install -r requirements.txt

# Check port 8000
netstat -ano | findstr :8000
```

### Frontend errors?

1. Press F12 → Console tab
2. Look for `[CallHistory]` messages
3. Check Network tab for failed requests

---

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/calls` | GET | Fetch call logs |
| `/calls/{id}` | GET | Get call details |
| `/calls/{id}` | DELETE | Delete call |
| `/calls` | DELETE | Delete all calls |
| `/health` | GET | System health |
| `/db-status` | GET | MongoDB status |

**Test:** http://localhost:8000/calls

---

## 🧪 Test Scripts

```bash
cd backend

# Test MongoDB connection
python test_mongodb_integration.py

# Test call logging
python test_call_logging.py

# Test REST API (backend must be running)
python test_rest_api.py

# Debug call history
python debug_call_history.py

# Fix old records
python fix_existing_records.py
```

---

## 📁 Key Files

```
backend/
├── main.py              # FastAPI server + Socket.io
├── models/Call.py       # MongoDB document model
├── logCall.py           # Call logging functions
├── config/db.py         # MongoDB connection
└── .env                 # MongoDB URI

frontend/src/
├── App.jsx              # Main app with tabs
└── components/
    └── CallHistoryView.jsx  # Call history UI
```

---

## 🎯 Layer 4 & 5 Compliance

### Layer 4: Longitudinal Learning ✅
- Call logs stored in MongoDB
- Phrase risk statistics
- Operator action tracking
- Pattern analysis ready

### Layer 5: Ethical Architecture ✅
- Privacy filtering (PII redacted)
- Audit trail with timestamps
- AI reasoning transparency
- Human-in-the-loop control

---

## 💡 Common Issues

| Issue | Solution |
|-------|----------|
| "No call logs found" | Create a call first |
| "Failed to fetch" | Start backend |
| "CORS error" | Check ALLOWED_ORIGINS |
| "Motor not found" | `pip install motor` |
| Port 8000 in use | Kill process or use different port |

---

## 📞 Quick Commands

```bash
# Check MongoDB has data
python backend/debug_call_history.py

# Start backend
cd backend && python main.py

# Start frontend
cd frontend && npm run dev

# Test API
curl http://localhost:8000/calls

# Check health
curl http://localhost:8000/health
```

---

## ✨ Demo Checklist

- [ ] Backend running (port 8000)
- [ ] Frontend running (port 5173)
- [ ] MongoDB connected
- [ ] Call History shows data
- [ ] Can create new calls
- [ ] Can delete calls
- [ ] Search works
- [ ] No console errors

**All checked? Ready to demo! 🎉**

---

## 📚 Full Documentation

- `START_SYSTEM.md` - Detailed startup guide
- `TROUBLESHOOT_CALL_HISTORY.md` - Step-by-step troubleshooting
- `CALL_HISTORY_FIXED.md` - What was fixed and how it works
- `MONGODB_INTEGRATION_COMPLETE.md` - Full implementation details
- `SYSTEM_ARCHITECTURE.md` - System architecture diagrams
- `FINAL_CHECKLIST.md` - Pre-demo checklist

---

**Status: ✅ READY FOR HACKATHON**

Time to demo: ~23 hours until judging 🚀
