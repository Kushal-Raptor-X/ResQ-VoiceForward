# 🚀 START HERE - Complete Setup Guide

**Current Status:** Sarvam AI integration complete, ready to test!

---

## 📋 Quick Decision Tree

**Choose your path:**

### Path A: Test with Live Microphone (Fastest - 10 min)
✅ Best for: Quick testing, immediate feedback
```bash
# Already configured! Just run:
cd backend
pip install -r requirements.txt
python main.py

# New terminal:
cd frontend
npm run dev

# Open: http://localhost:5173
# Speak into your mic!
```

### Path B: Record Demo Audio First (Recommended - 20 min)
✅ Best for: Presentations, repeatable demos
```bash
# 1. Test microphone
cd backend
python test_mic.py

# 2. Record demo (choose one):
python record_demo.py    # Interactive, 3 segments
# OR
python quick_record.py   # Quick, 90 seconds

# 3. Update .env:
# Change: AUDIO_SOURCE="backend/demo_audio/demo.wav"

# 4. Start backend
python main.py

# 5. Start frontend (new terminal)
cd ../frontend
npm run dev

# Open: http://localhost:5173
```

### Path C: Use Mock Data (Instant - 5 min)
✅ Best for: Testing UI without audio
```bash
# 1. Update .env:
# Change: USE_MOCK_TRANSCRIPTION="true"

# 2. Start backend
cd backend
python main.py

# 3. Start frontend (new terminal)
cd ../frontend
npm run dev

# Open: http://localhost:5173
```

---

## 🎯 Recommended Flow for Mentoring Demo

**Time: ~30 minutes total**

### Step 1: Install Dependencies (5 min)
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Test Sarvam API (2 min)
```bash
python test_sarvam.py
```
Expected: ✅ Transcription successful

### Step 3: Test Microphone (2 min)
```bash
python test_mic.py
```
Expected: ✅ Can record and play back

### Step 4: Record Demo Audio (10 min)
```bash
python record_demo.py
```
Follow prompts for 3 segments

### Step 5: Configure for Demo Mode (1 min)
Edit `backend/.env`:
```bash
AUDIO_SOURCE="backend/demo_audio/demo.wav"
```

### Step 6: Start Everything (2 min)
```bash
# Terminal 1
cd backend
python main.py

# Terminal 2
cd frontend
npm run dev
```

### Step 7: Verify Demo (5 min)
Open http://localhost:5173

Check:
- ✅ Transcript appears
- ✅ Risk phrases highlighted in red
- ✅ Risk indicator animates (LOW → MEDIUM → HIGH → CRITICAL)
- ✅ Agent cards show verdicts
- ✅ Suggested response appears
- ✅ No console errors

### Step 8: Practice Demo Narrative (5 min)
See talking points in `IMPLEMENTATION_COMPLETE.md`

---

## 📁 File Reference

### Configuration
- `backend/.env` - Environment variables (API keys, audio source)

### Testing
- `backend/test_mic.py` - Test microphone (5 seconds)
- `backend/test_sarvam.py` - Test Sarvam API
- `backend/test_audio_pipeline.py` - Test full pipeline

### Recording
- `backend/record_demo.py` - Interactive recorder (3 segments)
- `backend/quick_record.py` - Quick recorder (90 seconds)

### Running
- `backend/main.py` - Backend server
- `frontend/` - React frontend

### Documentation
- `START_HERE.md` - This file
- `QUICK_START.md` - 5-minute setup
- `RECORD_DEMO_AUDIO.md` - Recording guide
- `SARVAM_PIVOT_SUMMARY.md` - Technical details
- `IMPLEMENTATION_COMPLETE.md` - Full status

---

## 🎤 Audio Source Options

### Option 1: Live Microphone
**Config:** `AUDIO_SOURCE="mic"`

**Pros:**
- Real-time interaction
- No pre-recording needed
- Great for testing

**Cons:**
- Requires quiet environment
- Can have background noise
- Less predictable for demos

### Option 2: Pre-recorded Demo File
**Config:** `AUDIO_SOURCE="backend/demo_audio/demo.wav"`

**Pros:**
- Repeatable demo
- Perfect pacing
- No background noise
- Loops automatically

**Cons:**
- Requires recording first
- Takes 10-20 minutes to create

### Option 3: Mock Data
**Config:** `USE_MOCK_TRANSCRIPTION="true"`

**Pros:**
- Instant setup
- No audio needed
- Always works

**Cons:**
- Not real transcription
- Can't test Sarvam API
- Less impressive for demo

---

## 🐛 Common Issues

### "Module not found: aiohttp"
```bash
cd backend
pip install -r requirements.txt
```

### "Sarvam API error 401"
Check `backend/.env` has valid `SARVAM_API_KEY`

### "No microphone found"
- Check microphone is connected
- Grant permissions (Settings > Privacy > Microphone)
- Try: `python -m sounddevice` to list devices

### "Frontend not connecting"
- Check backend is running (port 8000)
- Check frontend is running (port 5173)
- Check browser console for errors

### "No transcript appearing"
- Check `USE_MOCK_TRANSCRIPTION="false"` in .env
- Check backend logs for errors
- Verify Sarvam API key is valid

### "Audio too quiet"
- Speak closer to microphone
- Increase system microphone volume
- Check microphone is not muted

---

## ✅ Success Checklist

### Before Mentoring (6 PM)
- [ ] Dependencies installed
- [ ] Sarvam API tested
- [ ] Demo audio recorded
- [ ] Backend starts without errors
- [ ] Frontend connects
- [ ] Transcript appears
- [ ] Risk highlighting works
- [ ] Prosody data visible in console
- [ ] Demo narrative prepared

### For Final Submission (10:45 AM Apr 12)
- [ ] Layer 1 fully working
- [ ] Layer 2 visible in UI
- [ ] Layer 3 polished
- [ ] Layer 5 documented
- [ ] README complete
- [ ] Demo runs smoothly

---

## 🎯 What to Show Mentors

### Opening (30 seconds)
> "VoiceForward is an AI copilot for crisis helpline operators. It listens to calls in real-time and provides multimodal analysis—not just what the caller says, but how they say it."

### Demo (2 minutes)
1. Show transcript appearing in real-time
2. Point out risk phrases highlighted in red
3. Show risk indicator animating LOW → HIGH → CRITICAL
4. Open browser console, show prosody data
5. Explain "unusual calm" detection

### Technical Deep Dive (2 minutes)
> "We're using Sarvam AI for transcription—optimized for Indian languages with native Hindi-English code-switching support. In parallel, we extract prosody features: speaking rate, pitch variance, energy. The system detected 'unusual calm' in the final segment—low energy, low pitch variance, slow rate—which research shows is a critical suicide risk indicator."

### Architecture (1 minute)
> "This is Layer 1—multimodal understanding. We're also building Layer 2 (multi-agent conflict resolution), Layer 3 (operator interface), and Layer 5 (ethical architecture with full audit trails)."

---

## 📞 Quick Commands

```bash
# Test microphone
cd backend && python test_mic.py

# Test Sarvam API
cd backend && python test_sarvam.py

# Record demo (interactive)
cd backend && python record_demo.py

# Record demo (quick)
cd backend && python quick_record.py

# Start backend
cd backend && python main.py

# Start frontend
cd frontend && npm run dev

# Open browser
http://localhost:5173
```

---

## ⏱️ Time Budget

**Current time:** ~12:30 PM
**Mentoring:** 6:00 PM
**Time remaining:** ~5.5 hours

**Recommended allocation:**
- 30 min: Setup and testing
- 20 min: Record demo audio
- 30 min: End-to-end verification
- 30 min: Fix any issues
- 30 min: Practice demo narrative
- 3 hours: Buffer / work on other layers

---

## 🚀 You're Ready!

Everything is implemented. Now just:
1. Test it works
2. Record your demo
3. Practice your narrative
4. Show the mentors

**You've got this! 💪**

---

**Need help?** Check the other docs:
- Quick setup: `QUICK_START.md`
- Recording: `RECORD_DEMO_AUDIO.md`
- Technical details: `SARVAM_PIVOT_SUMMARY.md`
- Full status: `IMPLEMENTATION_COMPLETE.md`
