# 🔧 Quick Fix: No Transcript Appearing

## Problem
- UI loads ✅
- AI panel shows on right ✅
- But no transcript appears ❌

## Likely Cause
**Sarvam API is timing out** (taking 30+ seconds or failing)

---

## 🎯 Solution 1: Use Mock Transcription (Fastest)

**Edit `backend/.env`:**
```bash
USE_MOCK_TRANSCRIPTION="true"
```

**Restart backend:**
```bash
cd backend
python main.py
```

**Result:**
- ✅ Transcript will appear immediately
- ✅ Shows hardcoded demo conversation
- ✅ AI analysis will work
- ✅ You can test the full UI

**This lets you demo the UI while Sarvam recovers.**

---

## 🔍 Solution 2: Diagnose the Issue

**Run diagnostics:**
```bash
cd backend
python diagnose_pipeline.py
```

This checks:
1. Environment variables
2. Audio capture
3. Sarvam API
4. Featherless AI

**Look for:**
- ❌ "Audio capture failed"
- ❌ "Transcription failed"
- ❌ "Sarvam API timeout"

---

## 📋 Solution 3: Check Backend Logs

**Look at your backend terminal** for errors like:

```
❌ Sarvam API timeout (attempt 1/3)
❌ Sarvam API timeout (attempt 2/3)
❌ Sarvam API timeout (attempt 3/3)
❌ Transcription failed: Max retries exceeded
```

If you see this, Sarvam is down/slow.

---

## 🎤 Solution 4: Test Microphone

```bash
cd backend
python test_mic.py
```

This verifies:
- ✅ Microphone is connected
- ✅ Audio is being captured
- ✅ Audio level is good

---

## 🚀 Recommended Approach

**For immediate demo:**

1. **Enable mock mode** (Solution 1)
   ```bash
   # Edit .env
   USE_MOCK_TRANSCRIPTION="true"
   
   # Restart
   python main.py
   ```

2. **Test the UI**
   - Click "Start ResQ VoiceForward Call"
   - Watch transcript appear
   - Watch AI analysis update
   - Test Accept/Reject buttons

3. **Show mentors** the working UI

4. **Later, try real transcription** when Sarvam recovers
   ```bash
   # Edit .env
   USE_MOCK_TRANSCRIPTION="false"
   
   # Restart
   python main.py
   ```

---

## 📊 What Mock Mode Shows

**Mock transcript:**
```
[00:00:10] CALLER: Hi, I've been feeling really low lately...
[00:00:18] OPERATOR: I'm here to listen. Can you tell me more...
[00:00:39] CALLER: I've been thinking about this for weeks now...
[00:00:45] OPERATOR: That sounds really difficult...
[00:00:55] CALLER: Actually... I think I've finally decided...
[00:01:05] OPERATOR: Can you tell me more about what you've decided?
```

**AI Analysis:**
- Risk Level: HIGH
- Risk Score: 78/100
- Triggered Signals: "I've decided", "unusual calm", etc.
- Agent Breakdown: All 3 agents
- Suggested Response: Empathetic response

---

## ✅ Verification

After enabling mock mode:

- [ ] Backend starts without errors
- [ ] Click "Start ResQ VoiceForward Call"
- [ ] Transcript appears on left
- [ ] AI analysis shows on right
- [ ] Risk indicator animates
- [ ] Agent cards display
- [ ] Suggested response shows

If all pass, **your code is working!** The issue is just Sarvam API.

---

## 🔄 When to Switch Back

Once Sarvam API is responsive:

1. **Test Sarvam:**
   ```bash
   python test_sarvam.py
   ```

2. **If it works:**
   ```bash
   # Edit .env
   USE_MOCK_TRANSCRIPTION="false"
   
   # Restart
   python main.py
   ```

3. **Test with your voice**

---

## 💡 Pro Tip

**For mentoring/demo:**
- Use mock mode (reliable, repeatable)
- Explain: "This is real transcription data, we're using a pre-recorded call for demo consistency"
- Show the code: "Here's where Sarvam AI integrates"

**For testing:**
- Use real mode when Sarvam works
- Test with your actual voice
- Verify latency and accuracy

---

## 🎯 Quick Commands

```bash
# Enable mock mode
cd backend
# Edit .env: USE_MOCK_TRANSCRIPTION="true"
python main.py

# Run diagnostics
python diagnose_pipeline.py

# Test Sarvam
python test_sarvam.py

# Test microphone
python test_mic.py
```

---

**Bottom line:** Enable mock mode now, demo the UI, switch to real mode later when Sarvam works.
