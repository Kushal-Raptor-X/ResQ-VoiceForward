#!/usr/bin/env python3
"""
Quick microphone test - records 5 seconds and plays back.
"""
import sounddevice as sd
import numpy as np

print("\n🎤 Microphone Test\n")

try:
    # List devices
    print("Available audio devices:")
    print(sd.query_devices())
    print("\n" + "="*70)
    
    # Get default input
    default_input = sd.query_devices(kind='input')
    print(f"\n✅ Default microphone: {default_input['name']}")
    
    input("\n📍 Press ENTER to record 5 seconds...")
    
    print("\n🔴 Recording... speak now!")
    
    # Record 5 seconds
    recording = sd.rec(
        int(5 * 16000),
        samplerate=16000,
        channels=1,
        dtype=np.float32
    )
    sd.wait()
    
    print("✅ Recording complete!")
    
    # Check if audio was captured
    max_amplitude = np.max(np.abs(recording))
    print(f"\n📊 Audio level: {max_amplitude:.4f}")
    
    if max_amplitude < 0.001:
        print("⚠️  WARNING: Audio level very low. Check:")
        print("   - Microphone is not muted")
        print("   - System volume is up")
        print("   - Speaking close to microphone")
    else:
        print("✅ Audio level looks good!")
    
    # Play back
    input("\n📍 Press ENTER to play back...")
    print("▶️  Playing...")
    sd.play(recording, 16000)
    sd.wait()
    
    print("\n✅ Microphone test complete!")
    print("\nNext: Run 'python record_demo.py' to create your demo audio")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check microphone is connected")
    print("  2. Grant microphone permissions")
    print("  3. Install sounddevice: pip install sounddevice")
