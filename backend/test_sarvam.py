#!/usr/bin/env python3
"""
Quick test script for Sarvam AI transcription.
Tests the transcriber with a synthetic audio chunk.
"""
import asyncio
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from transcriber import transcribe_chunk

async def test_sarvam():
    print("Testing Sarvam AI transcription...")
    
    # Check API key
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        print("\n❌ ERROR: SARVAM_API_KEY not found!")
        print("\nCheck that backend/.env file contains:")
        print('SARVAM_API_KEY="your_key_here"')
        return
    
    print(f"✅ API Key found: ...{api_key[-8:]}")
    
    # Generate 4 seconds of synthetic audio (silence for testing)
    sample_rate = 16000
    duration = 4.0
    audio_chunk = np.random.randn(int(sample_rate * duration)).astype(np.float32) * 0.01
    
    print(f"Audio chunk shape: {audio_chunk.shape}, dtype: {audio_chunk.dtype}")
    
    try:
        result = await transcribe_chunk(audio_chunk, sample_rate=sample_rate)
        
        print("\n✅ Transcription successful!")
        print(f"Text: {result['text']}")
        print(f"Language: {result['language']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Words: {len(result['words'])} words")
        
        if result['words']:
            print("\nFirst 3 words:")
            for word in result['words'][:3]:
                print(f"  - {word['word']} ({word['start']:.2f}s - {word['end']:.2f}s)")
    
    except Exception as e:
        print(f"\n❌ Transcription failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sarvam())
