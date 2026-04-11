# 🔬 Test Full Pipeline: Audio → AI Analysis

Two ways to test the complete flow:

---

## Option 1: AI Analyzer Test (Quick) ⚡

**Best for:** Verifying AI analysis works without microphone

```bash
cd backend
python test_analyzer.py
```

### What It Does
- Creates mock transcript with 3 segments
- Sends to Featherless AI (DeepSeek-V3)
- Shows risk analysis results
- Validates all components

### What You'll See
```
🤖 AI ANALYZER TEST

✅ API Key: ...4fe1a3e
📝 Creating mock transcript...
✅ Created 3 segments

📡 Sending to Featherless AI...
✅ Analysis complete in 3.45s

📊 ANALYSIS RESULTS

🚨 RISK LEVEL: HIGH
📊 RISK SCORE: 78/100
🎯 CONFIDENCE: HIGH

🔍 TRIGGERED SIGNALS:
  1. caller used phrase 'I've decided'
  2. speaking pace dropped 43%
  3. unusual calm detected

🤖 AGENT BREAKDOWN:
  • Language Agent: HIGH - passive farewell language
  • Emotion Agent: MEDIUM - flat affect
  • Narrative Agent: HIGH - story reached conclusion

💬 SUGGESTED RESPONSE:
  "It sounds like you've been carrying this..."

✅ ALL CHECKS PASSED!
```

**Time:** ~5 seconds

---

## Option 2: Full Pipeline Test (Complete) 🎤

**Best for:** Testing entire flow with real audio

```bash
cd backend
python test_full_pipeline.py
```

### What It Does
1. Records 3 audio chunks from microphone (4s each)
2. Transcribes each with Sarvam AI
3. Builds multimodal transcript
4. Analyzes with Featherless AI
5. Shows complete results

### What You'll See
```
🔬 FULL PIPELINE TEST
  Audio → Transcription → AI Analysis

✅ Sarvam API Key: ...jOROIiW2
✅ Featherless API Key: ...4fe1a3e
✅ Microphone: Microphone Array

TEST FLOW:
  1. Record audio from microphone
  2. Transcribe with Sarvam AI
  3. Analyze with Featherless AI
  4. Show risk analysis results

🔴 RECORDING... Speak naturally!

[CHUNK 1/3]
  🎤 Recording 4s...
  ✅ Audio captured (level: 0.123)
  📡 Transcribing with Sarvam AI...
  ✅ Transcribed: "Hi, I've been feeling really low lately"
     Language: en, Confidence: 95.2%
     Timing: 1.23s
  ✅ Segment added to session

[CHUNK 2/3]
  ...

[CHUNK 3/3]
  ...

📊 ANALYZING WITH AI...

✅ AI ANALYSIS COMPLETE

🚨 RISK LEVEL: MEDIUM
📊 RISK SCORE: 65/100
⏱️  ANALYSIS TIME: 3.21s

[Full analysis results...]

✅ FULL PIPELINE TEST COMPLETE
```

**Time:** ~30 seconds (12s recording + 5s transcription + 3s analysis)

---

## What Gets Tested

### Component Tests

| Component | Analyzer Test | Full Pipeline Test |
|-----------|--------------|-------------------|
| Sarvam AI Transcription | ❌ (mock data) | ✅ Real audio |
| Featherless AI Analysis | ✅ | ✅ |
| Multimodal Transcript | ✅ | ✅ |
| Risk Scoring | ✅ | ✅ |
| Agent Breakdown | ✅ | ✅ |
| Suggested Response | ✅ | ✅ |
| Word Timestamps | ❌ | ✅ |
| Prosody Features | ✅ (mock) | ✅ (real) |

---

## Expected Results

### AI Analyzer Test
- **Time:** 3-5 seconds
- **Risk Level:** HIGH (mock data has high-risk phrases)
- **Triggered Signals:** 3-5 signals
- **Agent Breakdown:** All 3 agents present
- **Suggested Response:** Present and relevant

### Full Pipeline Test
- **Recording:** 4s per chunk × 3 = 12s
- **Transcription:** ~1.5s per chunk × 3 = 4.5s
- **Analysis:** 3-5s
- **Total:** ~20-25s
- **Risk Level:** Depends on what you say
- **Accuracy:** 90%+ for clear speech

---

## Troubleshooting

### "FEATHERLESS_API_KEY not found"
Check `backend/.env` has:
```bash
FEATHERLESS_API_KEY="rc_7ab6513299dd2039b7faa982609e5331846cac72ff649c10b1ade438c4fe1a3e"
```

### "Analysis failed: timeout"
- Featherless API may be slow
- Try again in a few seconds
- Check internet connection

### "No segments to analyze"
- Speak louder (audio level too low)
- Check microphone is not muted
- Verify microphone permissions

### "Risk level not set"
- AI response may be malformed
- Check backend logs for JSON parsing errors
- Try running test again

---

## Validation Checklist

After running tests, verify:

### Analyzer Test
- [ ] API key found
- [ ] Analysis completes in < 10s
- [ ] Risk level is set (LOW/MEDIUM/HIGH/CRITICAL)
- [ ] Risk score is 0-100
- [ ] Triggered signals present (3+)
- [ ] Agent breakdown has 3 agents
- [ ] Suggested response present
- [ ] All validation checks pass

### Full Pipeline Test
- [ ] Microphone detected
- [ ] Audio captured (level > 0.001)
- [ ] Transcription successful
- [ ] Text matches what you said
- [ ] Language detected correctly
- [ ] Analysis completes
- [ ] Risk level appropriate for content
- [ ] Suggested response relevant

---

## What This Proves

### ✅ If Analyzer Test Passes
- Featherless AI API is working
- Risk analysis logic is correct
- Agent breakdown is functioning
- Suggested responses are generated
- JSON parsing is working

### ✅ If Full Pipeline Test Passes
- Sarvam AI transcription is working
- Audio capture is working
- Multimodal transcript building is correct
- End-to-end flow is functional
- **Ready for frontend integration!**

---

## Next Steps

### After Tests Pass

1. **Start the full application**
   ```bash
   # Terminal 1
   cd backend
   python main.py
   
   # Terminal 2
   cd frontend
   npm run dev
   ```

2. **Open browser**
   ```
   http://localhost:5173
   ```

3. **Verify in UI**
   - Transcript appears
   - Risk indicator animates
   - Agent cards show
   - Suggested response displays
   - Risk phrases highlighted

---

## Quick Commands

```bash
# Test AI analyzer (fast)
cd backend
python test_analyzer.py

# Test full pipeline (complete)
python test_full_pipeline.py

# Or use menu (Windows)
RUN_TESTS.bat
# Choose option 5 or 6
```

---

## 🎯 Recommended Testing Order

1. **test_analyzer.py** (5s) - Verify AI works
2. **test_full_pipeline.py** (30s) - Verify end-to-end
3. **Start full app** - Test with frontend

**Total time: ~2 minutes to full confidence!**

---

**Ready to test?**
```bash
cd backend
python test_analyzer.py
```

Then move to full pipeline test! 🚀
