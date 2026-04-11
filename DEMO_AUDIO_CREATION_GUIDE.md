# 🎙️ Demo Audio Creation Guide for VoiceForward

## Quick Start (Choose One Method)

### Method 1: ElevenLabs (RECOMMENDED - Fastest, Best Quality)
### Method 2: Google Cloud TTS with SSML
### Method 3: Record with Human Actors

---

## Method 1: ElevenLabs (RECOMMENDED)

**Time:** 15-20 minutes  
**Cost:** Free tier (10,000 characters/month)  
**Quality:** Excellent prosody control

### Step 1: Sign Up
1. Go to https://elevenlabs.io
2. Sign up for free account
3. Navigate to "Speech Synthesis"

### Step 2: Create Caller Voice (Segment 1 - Normal)

**Settings:**
- Voice: Choose "Adam" or "Antoni" (male, calm)
- Stability: 50%
- Clarity: 75%
- Style Exaggeration: 0%

**Text:**
```
Hi, I've been feeling really low lately. Work is tough, relationships aren't great. I don't know who to talk to.
```

**Download as:** `segment1_caller.mp3`

### Step 3: Create Operator Response (Segment 1)

**Settings:**
- Voice: Choose "Rachel" or "Bella" (female, professional)
- Stability: 70%
- Clarity: 80%

**Text:**
```
I'm here to listen. Can you tell me more about what's been happening?
```

**Download as:** `segment1_operator.mp3`

### Step 4: Create Caller Voice (Segment 2 - Slower, More Distressed)

**Settings:**
- Voice: Same as Segment 1
- Stability: 40% (more variation)
- Clarity: 70%
- Style Exaggeration: 20% (more emotional)

**Text:**
```
I've been thinking about this for weeks now. I just... I don't see a way forward anymore.
```

**Download as:** `segment2_caller.mp3`

### Step 5: Create Operator Response (Segment 2)

**Settings:**
- Voice: Same as Segment 1
- Stability: 70%
- Clarity: 80%

**Text:**
```
That sounds really difficult. What does 'a way forward' mean to you?
```

**Download as:** `segment2_operator.mp3`

### Step 6: Create Caller Voice (Segment 3 - CRITICAL: Unusual Calm)

**Settings:**
- Voice: Same as Segment 1
- Stability: 80% (very flat, monotone)
- Clarity: 60% (lower energy)
- Style Exaggeration: 0% (no emotion)
- **IMPORTANT:** Speak very slowly, very calmly

**Text:**
```
Actually... I think I've finally decided what I need to do. I feel very calm about it now.
```

**Download as:** `segment3_caller.mp3`

### Step 7: Create Operator Response (Segment 3)

**Settings:**
- Voice: Same as Segment 1
- Stability: 70%
- Clarity: 80%

**Text:**
```
Can you tell me more about what you've decided?
```

**Download as:** `segment3_operator.mp3`

### Step 8: Combine Audio Files

**On Windows (using ffmpeg):**
```bash
# Install ffmpeg first: https://ffmpeg.org/download.html

# Combine all segments
ffmpeg -i segment1_caller.mp3 -i segment1_operator.mp3 -i segment2_caller.mp3 -i segment2_operator.mp3 -i segment3_caller.mp3 -i segment3_operator.mp3 -filter_complex "[0:a][1:a][2:a][3:a][4:a][5:a]concat=n=6:v=0:a=1[out]" -map "[out]" -ar 16000 -ac 1 combined.wav

# Move to backend folder
move combined.wav backend\demo_audio\demo.wav
```

**On Mac/Linux:**
```bash
# Install ffmpeg: brew install ffmpeg (Mac) or sudo apt install ffmpeg (Linux)

# Combine all segments
ffmpeg -i segment1_caller.mp3 -i segment1_operator.mp3 -i segment2_caller.mp3 -i segment2_operator.mp3 -i segment3_caller.mp3 -i segment3_operator.mp3 -filter_complex "[0:a][1:a][2:a][3:a][4:a][5:a]concat=n=6:v=0:a=1[out]" -map "[out]" -ar 16000 -ac 1 combined.wav

# Move to backend folder
mv combined.wav backend/demo_audio/demo.wav
```

---

## Method 2: Google Cloud TTS with SSML

**Time:** 30-40 minutes  
**Cost:** Free tier ($300 credit)  
**Quality:** Good prosody control with SSML

### Step 1: Setup Google Cloud
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable "Cloud Text-to-Speech API"
4. Create service account and download JSON key

### Step 2: Install Google Cloud SDK
```bash
pip install google-cloud-texttospeech
```

### Step 3: Create Python Script

Save as `generate_demo_audio.py`:

```python
from google.cloud import texttospeech
import os

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your-key.json"

client = texttospeech.TextToSpeechClient()

# Segment 1 - Caller (Normal)
ssml1_caller = """
<speak>
  <prosody rate="medium" pitch="medium">
    Hi, I've been feeling really low lately. Work is tough, relationships aren't great. I don't know who to talk to.
  </prosody>
</speak>
"""

# Segment 1 - Operator
ssml1_operator = """
<speak>
  <prosody rate="medium" pitch="medium">
    I'm here to listen. Can you tell me more about what's been happening?
  </prosody>
</speak>
"""

# Segment 2 - Caller (Slower, more distressed)
ssml2_caller = """
<speak>
  <prosody rate="slow" pitch="low">
    I've been thinking about this for weeks now. <break time="500ms"/> I just... I don't see a way forward anymore.
  </prosody>
</speak>
"""

# Segment 2 - Operator
ssml2_operator = """
<speak>
  <prosody rate="medium" pitch="medium">
    That sounds really difficult. What does 'a way forward' mean to you?
  </prosody>
</speak>
"""

# Segment 3 - Caller (CRITICAL: Very slow, very calm, low energy)
ssml3_caller = """
<speak>
  <prosody rate="x-slow" pitch="low" volume="soft">
    Actually... <break time="800ms"/> I think I've finally decided what I need to do. <break time="500ms"/> I feel very calm about it now.
  </prosody>
</speak>
"""

# Segment 3 - Operator
ssml3_operator = """
<speak>
  <prosody rate="medium" pitch="medium">
    Can you tell me more about what you've decided?
  </prosody>
</speak>
"""

def synthesize_speech(ssml_text, output_file, voice_name="en-US-Standard-D"):
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000
    )
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    print(f"Created: {output_file}")

# Generate all segments
synthesize_speech(ssml1_caller, "segment1_caller.wav", "en-US-Standard-D")  # Male voice
synthesize_speech(ssml1_operator, "segment1_operator.wav", "en-US-Standard-F")  # Female voice
synthesize_speech(ssml2_caller, "segment2_caller.wav", "en-US-Standard-D")
synthesize_speech(ssml2_operator, "segment2_operator.wav", "en-US-Standard-F")
synthesize_speech(ssml3_caller, "segment3_caller.wav", "en-US-Standard-D")
synthesize_speech(ssml3_operator, "segment3_operator.wav", "en-US-Standard-F")

print("\nNow combine with ffmpeg:")
print("ffmpeg -i segment1_caller.wav -i segment1_operator.wav -i segment2_caller.wav -i segment2_operator.wav -i segment3_caller.wav -i segment3_operator.wav -filter_complex \"[0:a][1:a][2:a][3:a][4:a][5:a]concat=n=6:v=0:a=1[out]\" -map \"[out]\" backend/demo_audio/demo.wav")
```

### Step 4: Run Script
```bash
python generate_demo_audio.py
```

### Step 5: Combine with ffmpeg (same as Method 1, Step 8)

---

## Method 3: Record with Human Actors

**Time:** 45-60 minutes  
**Cost:** Free  
**Quality:** Most realistic, but requires acting skill

### Step 1: Setup Recording
1. Use Audacity (free): https://www.audacityteam.org/download/
2. Set project rate to 16000 Hz (bottom left)
3. Set to Mono recording

### Step 2: Record Script

**Caller (Male voice):**
- Segment 1: Normal pace, moderate emotion
- Segment 2: Slower pace, more distressed
- Segment 3: **VERY SLOW, VERY CALM, LOW ENERGY** (this is critical!)

**Operator (Female voice):**
- All segments: Professional, calm, empathetic

**Full Script:**
```
[0-10s] CALLER: Hi, I've been feeling really low lately. Work is tough, relationships aren't great. I don't know who to talk to.

[10-18s] OPERATOR: I'm here to listen. Can you tell me more about what's been happening?

[18-30s] CALLER: [slower] I've been thinking about this for weeks now. I just... I don't see a way forward anymore.

[30-40s] OPERATOR: That sounds really difficult. What does 'a way forward' mean to you?

[40-55s] CALLER: [very slow, very calm, low volume] Actually... I think I've finally decided what I need to do. I feel very calm about it now.

[55-65s] OPERATOR: Can you tell me more about what you've decided?
```

### Step 3: Export
1. File → Export → Export as WAV
2. Settings:
   - Sample Rate: 16000 Hz
   - Channels: Mono
   - Encoding: 16-bit PCM
3. Save as `backend/demo_audio/demo.wav`

---

## Verification Checklist

After creating demo.wav, verify:

- [ ] File exists at `backend/demo_audio/demo.wav`
- [ ] Duration: 60-90 seconds
- [ ] Sample rate: 16000 Hz (check with Audacity or ffmpeg)
- [ ] Channels: Mono
- [ ] Contains 3 distinct segments with escalating risk
- [ ] Segment 3 has noticeably slower, calmer speech
- [ ] No background noise or distortion
- [ ] Volume levels consistent across segments

**Check with ffmpeg:**
```bash
ffmpeg -i backend/demo_audio/demo.wav
```

Should show:
```
Duration: 00:01:05.00
Stream #0:0: Audio: pcm_s16le, 16000 Hz, 1 channels, s16, 256 kb/s
```

---

## Quick Test

Once created, test with Python:

```python
import scipy.io.wavfile as wav
import numpy as np

# Load audio
sample_rate, audio = wav.read("backend/demo_audio/demo.wav")

print(f"Sample rate: {sample_rate} Hz")
print(f"Duration: {len(audio) / sample_rate:.2f} seconds")
print(f"Channels: {audio.shape}")
print(f"Data type: {audio.dtype}")
print(f"Min/Max: {audio.min()}, {audio.max()}")

# Should output:
# Sample rate: 16000 Hz
# Duration: 65.00 seconds (or similar)
# Channels: (1040000,) or similar
# Data type: int16
```

---

## Troubleshooting

### Audio too quiet
```bash
ffmpeg -i demo.wav -filter:a "volume=2.0" demo_louder.wav
```

### Wrong sample rate
```bash
ffmpeg -i demo.wav -ar 16000 demo_16k.wav
```

### Stereo instead of mono
```bash
ffmpeg -i demo.wav -ac 1 demo_mono.wav
```

### File too large
```bash
# Compress to 16-bit PCM
ffmpeg -i demo.wav -acodec pcm_s16le demo_compressed.wav
```

---

## Expected Prosody Targets

Your demo audio should produce these approximate values when analyzed:

**Segment 1 (LOW risk):**
- Speaking rate: 130-150 wpm
- Pitch variance: 35-45 Hz
- Energy: -10 to -14 dB
- Unusual calm: False

**Segment 2 (MEDIUM→HIGH risk):**
- Speaking rate: 90-110 wpm
- Pitch variance: 20-30 Hz
- Energy: -13 to -16 dB
- Unusual calm: False (borderline)

**Segment 3 (CRITICAL risk):**
- Speaking rate: 70-90 wpm
- Pitch variance: 10-20 Hz
- Energy: -16 to -20 dB
- **Unusual calm: True** ← This is the key indicator!

---

## Time Estimate

- **Method 1 (ElevenLabs):** 15-20 minutes ⭐ RECOMMENDED
- **Method 2 (Google TTS):** 30-40 minutes
- **Method 3 (Human recording):** 45-60 minutes

**Recommendation:** Use Method 1 (ElevenLabs) for fastest, highest-quality results. The free tier is more than enough for this demo.

---

## Next Steps

Once you have `backend/demo_audio/demo.wav`:

1. ✅ Verify file with checklist above
2. ✅ Test with Python script
3. ✅ Proceed with Layer 1 implementation
4. ✅ Backend will automatically load and loop this file

**The implementation is starting now while you create this audio file!**
