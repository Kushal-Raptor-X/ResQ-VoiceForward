#!/usr/bin/env python3
"""
Quick 90-second demo audio recorder.
Just speak continuously for 90 seconds, no segments.
"""
import sounddevice as sd
import scipy.io.wavfile
import numpy as np
import time
import os

SAMPLE_RATE = 16000
DURATION = 90  # 90 seconds total
OUTPUT_FILE = "demo_audio/demo.wav"

def main():
    print("\n" + "="*70)
    print("  Quick Demo Audio Recorder (90 seconds)")
    print("="*70)
    
    print("\n📝 SCRIPT TO READ:")
    print("-" * 70)
    print("""
[First 30 seconds - Normal pace, moderate tone]
"Hi, I've been feeling really low lately. Work is tough, 
relationships aren't great. I don't know who to talk to.
I just feel overwhelmed sometimes. Everything feels like too much."

[Pause 3 seconds]

[Next 30 seconds - Slower pace, lower energy]
"I've been thinking about this... for weeks now. I just...
I don't see a way forward anymore. Nothing seems to help.
I've tried everything. I'm so tired of feeling this way."

[Pause 4 seconds]

[Final 30 seconds - Very slow, very quiet, flat tone]
"Actually... I think I've finally decided what I need to do.
I feel very calm about it now. It's like... everything is clear
for the first time. I just wanted to talk to someone one last time."

[Pause until time runs out]
""")
    print("-" * 70)
    
    # Check microphone
    try:
        default_input = sd.query_devices(kind='input')
        print(f"\n🎤 Using: {default_input['name']}")
    except Exception as e:
        print(f"\n❌ Microphone error: {e}")
        return
    
    # Create output directory
    os.makedirs("demo_audio", exist_ok=True)
    
    input("\n📍 Press ENTER when ready to record...")
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"\r🎤 Recording starts in {i}...", end="", flush=True)
        time.sleep(1)
    print("\r🔴 RECORDING NOW! (90 seconds)     ")
    print("=" * 70)
    
    # Record
    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.float32
    )
    
    # Progress bar
    for i in range(DURATION):
        remaining = DURATION - i
        bar_length = 50
        filled = int((i / DURATION) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r[{bar}] {i+1}/{DURATION}s", end="", flush=True)
        time.sleep(1)
    
    sd.wait()
    print("\n\n✅ Recording complete!")
    
    # Save
    audio_int16 = (recording * 32767).astype(np.int16)
    scipy.io.wavfile.write(OUTPUT_FILE, SAMPLE_RATE, audio_int16)
    
    print(f"\n💾 Saved to: {OUTPUT_FILE}")
    
    # Playback
    response = input("\n🔊 Play back? (y/n): ").lower()
    if response == 'y':
        print("▶️  Playing...")
        sd.play(recording, SAMPLE_RATE)
        sd.wait()
        print("✅ Done!")
    
    print("\n" + "="*70)
    print("🎉 Demo audio ready!")
    print("\nNext: Update .env with:")
    print('  AUDIO_SOURCE="backend/demo_audio/demo.wav"')
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
