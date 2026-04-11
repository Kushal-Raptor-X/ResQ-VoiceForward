#!/usr/bin/env python3
"""
Interactive demo audio recorder for VoiceForward.
Records 3 segments with prompts, saves as demo.wav
"""
import sounddevice as sd
import scipy.io.wavfile
import numpy as np
import time
import os

SAMPLE_RATE = 16000
OUTPUT_FILE = "demo_audio/demo.wav"

# Demo script with timing
SEGMENTS = [
    {
        "duration": 30,
        "risk": "LOW",
        "prompt": """
╔════════════════════════════════════════════════════════════════╗
║ SEGMENT 1 (30 seconds) - LOW RISK                             ║
╠════════════════════════════════════════════════════════════════╣
║ Speak naturally, moderate pace, normal tone                    ║
║                                                                ║
║ SUGGESTED SCRIPT:                                              ║
║ "Hi, I've been feeling really low lately. Work is tough,      ║
║  relationships aren't great. I don't know who to talk to."    ║
║                                                                ║
║ Then pause 2-3 seconds.                                        ║
║                                                                ║
║ "I just feel overwhelmed sometimes. Everything feels like     ║
║  too much."                                                    ║
╚════════════════════════════════════════════════════════════════╝
"""
    },
    {
        "duration": 30,
        "risk": "MEDIUM→HIGH",
        "prompt": """
╔════════════════════════════════════════════════════════════════╗
║ SEGMENT 2 (30 seconds) - MEDIUM→HIGH RISK                     ║
╠════════════════════════════════════════════════════════════════╣
║ Speak SLOWER, lower energy, more pauses                        ║
║                                                                ║
║ SUGGESTED SCRIPT:                                              ║
║ "I've been thinking about this... for weeks now."             ║
║                                                                ║
║ [Pause 3-4 seconds]                                            ║
║                                                                ║
║ "I just... I don't see a way forward anymore. Nothing seems   ║
║  to help. I've tried everything."                             ║
║                                                                ║
║ [Pause 2-3 seconds]                                            ║
║                                                                ║
║ "I'm so tired of feeling this way."                           ║
╚════════════════════════════════════════════════════════════════╝
"""
    },
    {
        "duration": 30,
        "risk": "CRITICAL",
        "prompt": """
╔════════════════════════════════════════════════════════════════╗
║ SEGMENT 3 (30 seconds) - CRITICAL RISK                        ║
╠════════════════════════════════════════════════════════════════╣
║ Speak VERY SLOWLY, VERY QUIET, FLAT TONE (unusual calm)       ║
║                                                                ║
║ SUGGESTED SCRIPT:                                              ║
║ "Actually... I think I've finally decided what I need to do." ║
║                                                                ║
║ [Pause 4-5 seconds]                                            ║
║                                                                ║
║ "I feel very calm about it now. It's like... everything is    ║
║  clear for the first time."                                   ║
║                                                                ║
║ [Pause 3-4 seconds]                                            ║
║                                                                ║
║ "I just wanted to talk to someone one last time."             ║
╚════════════════════════════════════════════════════════════════╝
"""
    }
]

def print_header():
    print("\n" + "="*70)
    print("  VoiceForward Demo Audio Recorder")
    print("="*70)
    print("\nThis will record 3 segments (30 seconds each) for your demo.")
    print("Follow the prompts to create realistic crisis call audio.\n")
    print("IMPORTANT TIPS:")
    print("  • Speak clearly into your microphone")
    print("  • Follow the pacing instructions (slow down in later segments)")
    print("  • Use pauses as indicated")
    print("  • Lower your voice energy in segment 3 (unusual calm)")
    print("\n" + "="*70 + "\n")

def countdown(seconds, message):
    """Visual countdown timer."""
    for i in range(seconds, 0, -1):
        print(f"\r{message} {i}s...", end="", flush=True)
        time.sleep(1)
    print(f"\r{message} NOW!     ")

def record_segment(segment_num, duration, prompt):
    """Record a single segment with prompts."""
    print(prompt)
    
    input(f"\n📍 Press ENTER when ready to record Segment {segment_num}...")
    
    countdown(3, "🎤 Recording starts in")
    
    print(f"\n🔴 RECORDING SEGMENT {segment_num} ({duration} seconds)")
    print("=" * 70)
    
    # Record audio
    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.float32
    )
    
    # Show progress
    for i in range(duration):
        remaining = duration - i
        bar_length = 50
        filled = int((i / duration) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r[{bar}] {i+1}/{duration}s", end="", flush=True)
        time.sleep(1)
    
    sd.wait()  # Wait for recording to finish
    print(f"\n\n✅ Segment {segment_num} recorded!\n")
    
    return recording

def preview_audio(audio, sample_rate):
    """Play back recorded audio."""
    response = input("🔊 Play back this segment? (y/n): ").lower()
    if response == 'y':
        print("▶️  Playing...")
        sd.play(audio, sample_rate)
        sd.wait()
        print("✅ Playback complete\n")

def main():
    print_header()
    
    # Check microphone
    try:
        devices = sd.query_devices()
        default_input = sd.query_devices(kind='input')
        print(f"🎤 Using microphone: {default_input['name']}\n")
    except Exception as e:
        print(f"❌ Error: Could not access microphone: {e}")
        print("\nTroubleshooting:")
        print("  1. Check microphone is connected")
        print("  2. Grant microphone permissions")
        print("  3. Try running: python -m sounddevice")
        return
    
    # Create output directory
    os.makedirs("demo_audio", exist_ok=True)
    
    # Record all segments
    all_audio = []
    
    for i, segment in enumerate(SEGMENTS, 1):
        while True:
            audio = record_segment(i, segment["duration"], segment["prompt"])
            preview_audio(audio, SAMPLE_RATE)
            
            response = input("✓ Keep this recording? (y/n/quit): ").lower()
            if response == 'y':
                all_audio.append(audio)
                break
            elif response == 'quit':
                print("\n❌ Recording cancelled.")
                return
            else:
                print("\n🔄 Re-recording segment...\n")
    
    # Concatenate all segments
    print("\n" + "="*70)
    print("📦 Combining segments...")
    full_audio = np.concatenate(all_audio)
    
    # Convert to int16 for WAV file
    audio_int16 = (full_audio * 32767).astype(np.int16)
    
    # Save to file
    scipy.io.wavfile.write(OUTPUT_FILE, SAMPLE_RATE, audio_int16)
    
    duration = len(full_audio) / SAMPLE_RATE
    print(f"✅ Demo audio saved to: {OUTPUT_FILE}")
    print(f"   Duration: {duration:.1f} seconds")
    print(f"   Sample rate: {SAMPLE_RATE} Hz")
    print(f"   Format: 16-bit mono WAV")
    
    # Play back full recording
    print("\n" + "="*70)
    response = input("🔊 Play back full recording? (y/n): ").lower()
    if response == 'y':
        print("▶️  Playing full demo audio...")
        sd.play(full_audio, SAMPLE_RATE)
        sd.wait()
        print("✅ Playback complete")
    
    print("\n" + "="*70)
    print("🎉 SUCCESS! Your demo audio is ready.")
    print("\nNext steps:")
    print("  1. Update .env: AUDIO_SOURCE=\"backend/demo_audio/demo.wav\"")
    print("  2. Restart backend: python main.py")
    print("  3. Open frontend: http://localhost:5173")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Recording cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
