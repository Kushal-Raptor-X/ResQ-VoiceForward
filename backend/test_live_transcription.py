#!/usr/bin/env python3
"""
Live transcription test - speak into mic, see transcription in real-time.
Tests Sarvam AI speed and accuracy.
"""
import asyncio
import sounddevice as sd
import numpy as np
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from transcriber import transcribe_chunk

SAMPLE_RATE = 16000
CHUNK_DURATION = 4  # 4 seconds per chunk

async def live_transcription_test():
    print("\n" + "="*70)
    print("  🎤 LIVE SARVAM AI TRANSCRIPTION TEST")
    print("="*70)
    
    # Check API key
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        print("\n❌ ERROR: SARVAM_API_KEY not found!")
        print("\nCheck that backend/.env file contains:")
        print('SARVAM_API_KEY="your_key_here"')
        return
    
    print(f"\n✅ API Key: ...{api_key[-8:]}")
    print("\nThis will transcribe your speech in real-time.")
    print("Speak naturally and watch the transcription appear.\n")
    print("Press Ctrl+C to stop.\n")
    print("="*70 + "\n")
    
    # Check microphone
    try:
        default_input = sd.query_devices(kind='input')
        print(f"🎤 Using: {default_input['name']}\n")
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return
    
    input("📍 Press ENTER to start live transcription...")
    print("\n🔴 LISTENING... (speak now)\n")
    print("="*70)
    
    chunk_num = 0
    context = ""
    
    try:
        while True:
            chunk_num += 1
            
            # Record chunk
            print(f"\n[Chunk {chunk_num}] Recording {CHUNK_DURATION}s...")
            t_start = time.time()
            
            audio = sd.rec(
                int(CHUNK_DURATION * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            t_record = time.time()
            
            # Check audio level
            max_amp = np.max(np.abs(audio))
            if max_amp < 0.001:
                print("⚠️  [Silent - skipping]")
                continue
            
            # Transcribe
            print(f"📡 Calling Sarvam API...")
            result = await transcribe_chunk(audio, SAMPLE_RATE, context)
            t_transcribe = time.time()
            
            # Display results
            if result['text']:
                print(f"\n✅ TRANSCRIPTION:")
                print(f"   Text: {result['text']}")
                print(f"   Language: {result['language']}")
                print(f"   Confidence: {result['confidence']:.2%}")
                print(f"   Words: {len(result['words'])}")
                
                # Show timing
                record_time = t_record - t_start
                api_time = t_transcribe - t_record
                total_time = t_transcribe - t_start
                
                print(f"\n⏱️  TIMING:")
                print(f"   Recording: {record_time:.2f}s")
                print(f"   Sarvam API: {api_time:.2f}s")
                print(f"   Total: {total_time:.2f}s")
                
                if total_time < 3.0:
                    print(f"   ✅ Under 3s target!")
                else:
                    print(f"   ⚠️  Over 3s target")
                
                # Show first few words with timestamps
                if result['words']:
                    print(f"\n📝 WORD TIMESTAMPS (first 5):")
                    for word in result['words'][:5]:
                        print(f"   {word['start']:.2f}s - {word['end']:.2f}s: \"{word['word']}\" ({word['confidence']:.2%})")
                
                # Update context for next chunk
                context = result['text']
            else:
                print("⚠️  No transcription (silence or API error)")
            
            print("\n" + "="*70)
    
    except KeyboardInterrupt:
        print("\n\n✅ Test stopped by user")
        print("\n" + "="*70)
        print("SUMMARY:")
        print(f"  Total chunks processed: {chunk_num}")
        print("="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(live_transcription_test())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
