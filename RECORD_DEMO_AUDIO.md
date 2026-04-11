# 🎤 Record Demo Audio with Your Microphone

You have **two options** for recording demo audio:

---

## Option 1: Interactive Recorder (Recommended) ⭐

**Best for:** Creating high-quality demo with proper pacing

### Features
- Records 3 separate segments (30s each)
- Shows script prompts for each segment
- Lets you re-record any segment
- Preview before saving
- Guides you on pacing and tone

### Usage
```bash
cd backend
python record_demo.py
```

### What It Does
1. Shows you the script for Segment 1 (LOW risk)
2. Counts down 3... 2... 1...
3. Records for 30 seconds with progress bar
4. Lets you preview and re-record if needed
5. Repeats for Segments 2 and 3
6. Combines all segments into `demo_audio/demo.wav`

### Tips
- **Segment 1:** Speak normally, moderate pace
- **Segment 2:** Slow down, lower energy, add pauses
- **Segment 3:** Very slow, very quiet, flat tone (unusual calm)

---

## Option 2: Quick Recorder (Fast) ⚡

**Best for:** Quick testing, one continuous take

### Features
- Single 90-second recording
- Shows full script upfront
- No segments, just read continuously
- Faster workflow

### Usage
```bash
cd backend
python quick_record.py
```

### What It Does
1. Shows you the full 90-second script
2. Counts down 3... 2... 1...
3. Records for 90 seconds straight
4. Saves to `demo_audio/demo.wav`

### Tips
- Read the script naturally
- Remember to slow down and quiet down in the final 30 seconds
- Use pauses as indicated

---

## After Recording

### 1. Update Configuration
Edit `backend/.env`:
```bash
AUDIO_SOURCE="backend/demo_audio/demo.wav"
```

### 2. Test the Audio
```bash
cd backend
python main.py
```

Then open frontend:
```bash
cd frontend
npm run dev
```

Go to http://localhost:5173 and verify:
- ✅ Transcript appears
- ✅ Risk phrases highlighted
- ✅ Risk indicator changes across segments
- ✅ Prosody features detected

---

## Troubleshooting

### "No microphone found"
**Windows:**
```bash
# Check microphone in Settings > Privacy > Microphone
# Grant permission to Python
```

**Mac:**
```bash
# System Preferences > Security & Privacy > Microphone
# Allow Terminal/Python
```

**Linux:**
```bash
# Check ALSA/PulseAudio
arecord -l
```

### "Module 'sounddevice' not found"
```bash
cd backend
pip install sounddevice scipy numpy
```

### "Recording is too quiet"
- Speak closer to microphone
- Increase system microphone volume
- Check microphone is not muted

### "Recording has background noise"
- Use a quiet room
- Close windows/doors
- Turn off fans/AC temporarily
- Use headset microphone if available

---

## Alternative: Use Live Microphone

If you don't want to pre-record, you can use live microphone mode:

### In `.env`:
```bash
AUDIO_SOURCE="mic"
```

### Then:
1. Start backend: `python main.py`
2. Start frontend: `npm run dev`
3. Open http://localhost:5173
4. Speak into your microphone
5. Transcript appears in real-time

**Note:** Live mode is great for testing but pre-recorded demo is better for presentations (more reliable, repeatable).

---

## Script Reference

### Segment 1 (0-30s) - LOW RISK
```
"Hi, I've been feeling really low lately. Work is tough,
relationships aren't great. I don't know who to talk to.
I just feel overwhelmed sometimes. Everything feels like too much."
```

**Pacing:** Normal (140 wpm)
**Tone:** Moderate energy
**Pitch:** Normal variance

---

### Segment 2 (30-60s) - MEDIUM→HIGH RISK
```
"I've been thinking about this... for weeks now. I just...
I don't see a way forward anymore. Nothing seems to help.
I've tried everything. I'm so tired of feeling this way."
```

**Pacing:** Slower (100 wpm)
**Tone:** Lower energy
**Pitch:** Less variance
**Pauses:** 3-4 seconds between sentences

---

### Segment 3 (60-90s) - CRITICAL RISK
```
"Actually... I think I've finally decided what I need to do.
I feel very calm about it now. It's like... everything is clear
for the first time. I just wanted to talk to someone one last time."
```

**Pacing:** Very slow (80 wpm)
**Tone:** Very quiet, flat (unusual calm)
**Pitch:** Minimal variance
**Pauses:** 4-5 seconds between sentences

---

## Expected Results

When you play the demo, you should see:

### Segment 1
- Risk Level: **LOW** (score ~30)
- Speaking rate: ~140 wpm
- Pitch variance: ~40 Hz
- Energy: ~-12 dB

### Segment 2
- Risk Level: **MEDIUM→HIGH** (score ~65)
- Speaking rate: ~100 wpm (↓29%)
- Pitch variance: ~25 Hz (↓38%)
- Energy: ~-15 dB
- Triggered signals: "speaking pace dropped", "phrase 'no way forward'"

### Segment 3
- Risk Level: **CRITICAL** (score ~92)
- Speaking rate: ~80 wpm (↓43%)
- Pitch variance: ~15 Hz (↓63%)
- Energy: ~-18 dB
- **Unusual calm: TRUE** ← Key indicator!
- Triggered signals: "unusual calm detected", "phrase 'I've decided'"

---

## Quick Start

**Fastest path to working demo:**

```bash
# 1. Record audio (5 minutes)
cd backend
python quick_record.py

# 2. Update config
# Edit .env: AUDIO_SOURCE="backend/demo_audio/demo.wav"

# 3. Start backend
python main.py

# 4. Start frontend (new terminal)
cd ../frontend
npm run dev

# 5. Open browser
# http://localhost:5173
```

**Total time: ~10 minutes**

---

## Need Help?

- **Can't record?** Use live mic mode: `AUDIO_SOURCE="mic"`
- **No microphone?** Use mock mode: `USE_MOCK_TRANSCRIPTION="true"`
- **Recording failed?** Check `python -m sounddevice` for device list

---

**You've got this! Record your demo and show the mentors! 🎤🚀**
