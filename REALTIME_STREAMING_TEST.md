# Real-Time Streaming - Testing Guide

## What Changed

### Audio Chunking
- **Before**: 8-second chunks → wait → display
- **After**: 100ms chunks → continuous stream → real-time display

### Speaker Detection
- **Before**: Alternating CALLER/OPERATOR (unrealistic)
- **After**: All marked as CALLER (realistic for single-person demo)
- **Future**: Speaker diarization to distinguish voices

## How to Test

### 1. Start Backend
```bash
cd backend
python main.py
```

You should see:
```
Sarvam AI WebSocket transcriber initialized (Saaras V3, key: ...iW2)
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Real-Time Transcription

1. Open browser to `http://localhost:5173`
2. Click **"Start Call Transcript"**
3. **Speak into your microphone**
4. Watch the transcript panel

### Expected Behavior

**Real-time flow:**
```
You speak: "Hello, I've been feeling..."
↓ (100-200ms later)
Transcript appears: "Hello, I've been feeling..."
↓ (you continue)
"...really stressed lately"
↓ (appears immediately)
Transcript updates: "Hello, I've been feeling really stressed lately"
```

**NOT chunky:**
```
❌ You speak for 8 seconds → wait → all text appears at once
✅ You speak → text appears as you speak → smooth flow
```

## Troubleshooting

### Issue: Still seeing 8-second delays

**Check:**
1. Backend restarted? (old code might be cached)
2. WebSocket connected? Look for: `✓ WebSocket connected to Sarvam`
3. Audio source? Check `.env` file: `AUDIO_SOURCE="mic"`

**Fix:**
```bash
# Kill backend
Ctrl+C

# Restart
python main.py
```

### Issue: No transcription appearing

**Check logs for:**
```
✓ WebSocket connected to Sarvam (mode=transcribe, lang=en-IN)
🎤 Speech detected
→ Partial: Hello...
✓ Transcript: [CALLER] Hello, I've been feeling really stressed lately
```

**If you see:**
```
WebSocket connection failed: ...
```

**Possible causes:**
1. No internet connection
2. Sarvam API key invalid
3. Sarvam API down

### Issue: Microphone not working

**Check:**
1. Browser permissions: Allow microphone access
2. System permissions: Microphone enabled for terminal/app
3. Fallback: Set `AUDIO_SOURCE="backend/demo_audio/demo.wav"` in `.env`

## Performance Metrics

### Real-Time Streaming (Current)
- **First token latency**: 100-300ms
- **Chunk size**: 100ms (1,600 samples)
- **Network overhead**: Minimal (small chunks)
- **User experience**: Smooth, professional

### Batch Processing (Old)
- **First token latency**: 8-30 seconds
- **Chunk size**: 8 seconds (128,000 samples)
- **Network overhead**: High (large chunks)
- **User experience**: Chunky, delayed

## Demo Script

For hackathon judges:

1. **Show the interface**: "This is VoiceForward, a real-time AI copilot for crisis helpline operators"

2. **Click Start Call**: "When a call begins, the system starts listening"

3. **Speak naturally**: "I've been feeling really stressed lately. Work has been overwhelming and I don't know who to talk to."

4. **Point to transcript**: "Notice how the transcript appears in real-time as I speak - not in chunks"

5. **Point to risk panel**: "The AI analyzes the conversation continuously and updates the risk assessment"

6. **Show suggestions**: "It provides the operator with suggested responses based on the context"

## Technical Details

### WebSocket Flow
```
Microphone (100ms chunks)
    ↓
Audio Capture (numpy arrays)
    ↓
Convert to WAV bytes
    ↓
WebSocket → Sarvam V3
    ↓
Partial transcripts (while speaking)
    ↓
Final transcript (on speech pause)
    ↓
Frontend display
```

### VAD (Voice Activity Detection)
- Detects when speech starts
- Detects when speech ends (silence)
- Emits final transcript on speech pause
- Sensitivity: Standard (1 second silence)

### Speaker Detection
- **Current**: All marked as CALLER
- **Why**: Single-person demo, realistic
- **Production**: Use speaker diarization API
  - Sarvam Batch API supports speaker diarization
  - Or use voice fingerprinting
  - Or manual operator button to mark their speech

## Next Steps (Optional Enhancements)

### 1. Show Partial Transcripts
Display gray text while speaking, solidify on final:
```jsx
<span className={isPartial ? "text-gray-500 italic" : "text-white"}>
  {text}
</span>
```

### 2. Word-Level Highlighting
Highlight words as they're spoken using timestamps

### 3. Multi-Language Support
Switch between Hindi/English dynamically

### 4. Translation Mode
Use `mode=translate` for Hindi→English translation

---

**Status**: ✅ Real-time streaming enabled
**Test it**: Speak and watch text appear live!
