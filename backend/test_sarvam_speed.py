#!/usr/bin/env python3
"""
Test Sarvam AI speed with synthetic audio.
Shows API latency without needing to speak.
"""
import asyncio
import numpy as np
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from transcriber import transcribe_chunk

async def test_api_speed():
    print("\n" + "="*70)
    print("  ⚡ SARVAM AI SPEED TEST")
    print("="*70)
    
    # Check API key
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        print("\n❌ ERROR: SARVAM_API_KEY not found!")
        print("\nCheck that backend/.env file contains:")
        print('SARVAM_API_KEY="your_key_here"')
        return
    
    print(f"\n✅ API Key: ...{api_key[-8:]}")
    print("\nTesting API latency with synthetic audio...\n")
    
    # Generate 4 seconds of synthetic audio (white noise)
    sample_rate = 16000
    duration = 4.0
    audio = np.random.randn(int(sample_rate * duration)).astype(np.float32) * 0.1
    
    print(f"📊 Audio: {duration}s, {sample_rate}Hz, {audio.shape[0]} samples")
    print(f"   Format: {audio.dtype}, range: [{audio.min():.3f}, {audio.max():.3f}]")
    
    # Run 3 tests
    print("\n" + "="*70)
    print("Running 3 API calls...\n")
    
    times = []
    
    for i in range(1, 4):
        print(f"Test {i}/3:")
        
        t_start = time.time()
        result = await transcribe_chunk(audio, sample_rate)
        t_end = time.time()
        
        elapsed = t_end - t_start
        times.append(elapsed)
        
        print(f"  ⏱️  Time: {elapsed:.2f}s")
        print(f"  📝 Text: {result['text'][:50]}..." if result['text'] else "  ⚠️  No text (expected for noise)")
        print(f"  🌐 Language: {result['language']}")
        print(f"  ✅ Confidence: {result['confidence']:.2%}")
        print()
    
    # Summary
    print("="*70)
    print("RESULTS:")
    print(f"  Average latency: {np.mean(times):.2f}s")
    print(f"  Min latency: {np.min(times):.2f}s")
    print(f"  Max latency: {np.max(times):.2f}s")
    
    avg_time = np.mean(times)
    if avg_time < 1.5:
        print(f"  ✅ EXCELLENT - Under 1.5s!")
    elif avg_time < 2.0:
        print(f"  ✅ GOOD - Under 2.0s")
    elif avg_time < 3.0:
        print(f"  ⚠️  OK - Under 3.0s target")
    else:
        print(f"  ❌ SLOW - Over 3.0s target")
    
    print("\n💡 Note: This is synthetic noise, not real speech.")
    print("   Real speech transcription may be faster/slower.")
    print("   Run 'python test_live_transcription.py' to test with your voice.")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_api_speed())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
