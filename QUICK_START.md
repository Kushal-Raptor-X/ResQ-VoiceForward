# VoiceForward - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- Sarvam API key (already in `.env`)

---

## Step 1: Install Backend Dependencies (2 min)

```bash
cd backend
pip install -r requirements.txt
```

**What this installs:**
- `aiohttp` - Sarvam AI API calls
- `sounddevice` - Audio capture
- `scipy` - Audio processing
- `librosa` - Prosody feature extraction
- `fastapi` - Backend server
- Other dependencies

---

## Step 2: Verify Configuration (30 sec)

Check `backend/.env` has:
```bash
SARVAM_API_KEY="sk_0phoriyn_LqFU7OQoxPMXqKecjOROIiW2"
AUDIO_SOURCE="mic"
USE_MOCK_TRANSCRIPTION="false"
FEATHERLESS_API_KEY="rc_7ab6513299dd2039b7faa982609e5331846cac72ff649c10b1ade438c4fe1a3e"
```

✅ All set!

---

## Step 3: Test Sarvam API (1 min)

```bash
cd backend
python test_sarvam.py
```

**Expected output:**
```
Testing Sarvam AI transcription...
Audio chunk shape: (64000,), dtype: float32

✅ Transcription successful!
Text: [transcribed text]
Language: en
Confidence: 0.95
Words: X words
```

If you see errors, check:
- Internet connection (Sarvam is cloud-based)
- API key is valid
- No firewall blocking API calls

---

## Step 4: Start Backend Server (30 sec)

```bash
cd backend
python main.py
```

**Expected output:**
```
INFO:transcriber:Sarvam AI transcriber initialized
INFO:uvicorn.error:Uvicorn running on http://127.0.0.1:8000
```

Leave this running!

---

## Step 5: Start Frontend (1 min)

Open a **new terminal**:

```bash
cd frontend
npm install  # First time only
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
```

---

## Step 6: Open Browser

Go to: **http://localhost:5173**

You should see:
- Split-screen dashboard
- Transcript panel (left)
- Risk indicator (right)
- Agent cards
- Suggestion card

---

## 🎤 Audio Modes

### Mode 1: Microphone (Live)
- Browser will ask for mic permission
- Speak into your microphone
- Transcript appears in real-time

### Mode 2: Demo File (Recommended for Demo)
1. Create `backend/demo_audio/demo.wav` (see `DEMO_AUDIO_CREATION_GUIDE.md`)
2. Set `AUDIO_SOURCE="backend/demo_audio/demo.wav"` in `.env`
3. Restart backend
4. Demo audio plays and loops automatically

### Mode 3: Mock Data (Fallback)
- Set `USE_MOCK_TRANSCRIPTION="true"` in `.env`
- Uses hardcoded transcript
- No audio processing needed

---

## 🐛 Troubleshooting

### "Module not found: aiohttp"
```bash
cd backend
pip install aiohttp
```

### "Sarvam API error 401"
- Check API key in `.env`
- Verify key is valid at https://sarvam.ai

### "Frontend not connecting"
- Check backend is running on port 8000
- Check browser console for errors
- Verify CORS settings (should be automatic)

### "No transcript appearing"
- Check browser console for Socket.io connection
- Verify `USE_MOCK_TRANSCRIPTION="false"` in `.env`
- Check backend logs for errors

### "Microphone not working"
- Grant browser microphone permission
- Check system audio settings
- Fallback: use demo file mode

---

## 📊 What to Check

### Backend Logs
Look for:
- ✅ "Sarvam AI transcriber initialized"
- ✅ "Client connected: [sid]"
- ✅ "Transcription complete: text='...'"
- ❌ Any ERROR messages

### Frontend Console
Look for:
- ✅ Socket.io connection established
- ✅ "transcript_update" events
- ✅ "analysis_update" events
- ❌ Any red errors

### UI Elements
Verify:
- ✅ Transcript lines appearing
- ✅ Risk indicator animating
- ✅ Agent cards showing verdicts
- ✅ Suggested response visible
- ✅ Risk phrases highlighted in red

---

## 🎯 Success Criteria

You're ready for demo when:
- [ ] Backend starts without errors
- [ ] Frontend loads and connects
- [ ] Transcript appears (mock or real)
- [ ] Risk indicator shows color
- [ ] Agent cards display
- [ ] No console errors

---

## 📞 Next Steps

1. **Create demo audio** - Follow `DEMO_AUDIO_CREATION_GUIDE.md`
2. **Test end-to-end** - Verify all features work
3. **Practice demo** - Prepare talking points
4. **Show mentors** - 6 PM mentoring session

---

## 🔥 Quick Commands Reference

```bash
# Backend
cd backend
pip install -r requirements.txt
python test_sarvam.py
python main.py

# Frontend
cd frontend
npm install
npm run dev

# Open browser
http://localhost:5173
```

---

**Time to get running: ~5 minutes**
**Time to full demo: ~90 minutes (including audio creation)**

You've got this! 🚀
