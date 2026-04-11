# 🧪 Test Sarvam AI Speed & Accuracy

Three ways to test Sarvam AI transcription:

---

## Option 1: Live Transcription Test (Recommended) ⭐

**Best for:** Testing real speech accuracy and speed

```bash
cd backend
python test_live_transcription.py
```

### What It Does
- Records 4-second chunks from your microphone
- Sends to Sarvam API
- Shows transcription in real-time
- Displays timing breakdown
- Shows word-level timestamps
- Continues until you press Ctrl+C

### What You'll See
```
[Chunk 1] Recording 4s...
📡 Calling Sarvam API...

✅ TRANSCRIPTION:
   Text: I've been feeling really low lately
   Language: en
   Confidence: 95.23%
   Words: 6

⏱️  TIMING:
   Recording: 4.00s
   Sarvam API: 1.23s
   Total: 5.23s
   ✅ Under 3s target!

📝 WORD TIMESTAMPS (first 5):
   0.00s - 0.20s: "I've" (96.50%)
   0.20s - 0.40s: "been" (98.20%)
   ...
```

### Tips
- Speak clearly and naturally
- Try different pacing (fast, slow)
- Test Hindi-English code-switching
- Watch the timing - should be under 3s total
- Press Ctrl+C to stop

---

## Option 2: Speed Test (No Speaking Required)

**Best for:** Testing API latency without microphone

```bash
cd backend
python test_sarvam_speed.py
```

### What It Does
- Generates synthetic audio
- Calls Sarvam API 3 times
- Shows average latency
- No microphone needed

### What You'll See
```
Running 3 API calls...

Test 1/3:
  ⏱️  Time: 1.23s
  📝 Text: [transcribed noise]
  🌐 Language: en
  ✅ Confidence: 45.67%

RESULTS:
  Average latency: 1.25s
  Min latency: 1.18s
  Max latency: 1.34s
  ✅ EXCELLENT - Under 1.5s!
```

---

## Option 3: Basic API Test

**Best for:** Verifying API connection

```bash
cd backend
python test_sarvam.py
```

### What It Does
- Single API call with synthetic audio
- Verifies API key works
- Shows basic response format

---

## 🎯 What to Look For

### Speed (Latency)
- ✅ **Excellent:** < 1.5s
- ✅ **Good:** 1.5s - 2.0s
- ⚠️ **OK:** 2.0s - 3.0s
- ❌ **Slow:** > 3.0s

**Note:** Total latency includes recording time (4s). API call itself should be 1-2s.

### Accuracy
- ✅ **Excellent:** 95%+ confidence, perfect transcription
- ✅ **Good:** 85-95% confidence, minor errors
- ⚠️ **OK:** 70-85% confidence, some errors
- ❌ **Poor:** < 70% confidence, many errors

### Word Timestamps
- Should align with when you spoke each word
- Start/end times should be reasonable (0.1-0.5s per word)
- Confidence per word should be high (>90%)

---

## 🧪 Test Scenarios

### Test 1: Normal Speech
Speak at normal pace:
> "Hi, I've been feeling really low lately. Work is tough."

**Expected:**
- Latency: ~1.5s
- Confidence: >95%
- All words captured

### Test 2: Slow Speech
Speak very slowly with pauses:
> "I've been... thinking about this... for weeks now."

**Expected:**
- Latency: ~1.5s
- Confidence: >90%
- Pauses preserved

### Test 3: Fast Speech
Speak quickly:
> "I don't know what to do everything is overwhelming"

**Expected:**
- Latency: ~1.5s
- Confidence: >85%
- May miss some words

### Test 4: Hindi-English Code-Switching
Mix languages:
> "I'm feeling bahut low, kuch samajh nahi aa raha"

**Expected:**
- Latency: ~1.5s
- Language: "en" or "hi" (may switch)
- Both languages transcribed

### Test 5: Quiet Speech (Unusual Calm)
Speak very quietly and slowly:
> "I think I've finally decided what I need to do."

**Expected:**
- Latency: ~1.5s
- Confidence: may be lower (80-90%)
- Should still transcribe

---

## 🐛 Troubleshooting

### "SARVAM_API_KEY not configured"
Check `backend/.env` has:
```bash
SARVAM_API_KEY="sk_0phoriyn_LqFU7OQoxPMXqKecjOROIiW2"
```

### "Sarvam API error 401"
- API key is invalid
- Check https://sarvam.ai for account status

### "Sarvam API timeout"
- Network connection slow
- API may be under load
- Try again in a few seconds

### "No transcription (silence or API error)"
- Audio level too low (speak louder)
- Microphone muted
- Check backend logs for errors

### "Latency > 3s"
- Network connection slow
- API under load
- Normal - includes 4s recording time

---

## 📊 Expected Performance

### Typical Results
```
Recording: 4.00s (fixed - chunk duration)
Sarvam API: 1.0-1.5s (network + processing)
Total: 5.0-5.5s

Actual transcription latency: 1.0-1.5s ✅
```

### Comparison with Whisper
| Metric | Whisper (local) | Sarvam AI |
|--------|----------------|-----------|
| Latency | 1.5-2.0s | 1.0-1.5s |
| Accuracy (English) | 95%+ | 95%+ |
| Accuracy (Hindi) | 85-90% | 95%+ |
| Code-switching | Good | Excellent |
| Setup time | 2-5s (model load) | <1s |

---

## ✅ Success Criteria

You're ready to proceed if:
- [ ] API calls complete successfully
- [ ] Latency is under 2s (API call only)
- [ ] Transcription accuracy is >90%
- [ ] Word timestamps are present
- [ ] Hindi/English both work

---

## 🚀 Next Steps

Once you've verified Sarvam AI works well:

1. **Record demo audio**
   ```bash
   python record_demo.py
   ```

2. **Start full pipeline**
   ```bash
   python main.py
   ```

3. **Test with frontend**
   ```bash
   cd ../frontend && npm run dev
   ```

---

## 💡 Quick Commands

```bash
# Live transcription (speak into mic)
cd backend
python test_live_transcription.py

# Speed test (no mic needed)
python test_sarvam_speed.py

# Basic API test
python test_sarvam.py

# Test microphone
python test_mic.py
```

---

**Ready to test? Start with:**
```bash
cd backend
python test_live_transcription.py
```

Speak naturally and watch the magic happen! 🎤✨
