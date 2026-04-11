#!/usr/bin/env python3
"""
Diagnose the audio pipeline - check each component.
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def diagnose():
    print("\n" + "="*70)
    print("  🔍 AUDIO PIPELINE DIAGNOSTICS")
    print("="*70)
    
    # Check 1: Environment
    print("\n1️⃣  ENVIRONMENT CHECK")
    print("-" * 70)
    
    sarvam_key = os.getenv("SARVAM_API_KEY")
    featherless_key = os.getenv("FEATHERLESS_API_KEY")
    audio_source = os.getenv("AUDIO_SOURCE", "mic")
    use_mock = os.getenv("USE_MOCK_TRANSCRIPTION", "false").lower() == "true"
    
    print(f"  Sarvam API Key: {'✅' if sarvam_key else '❌'} ...{sarvam_key[-8:] if sarvam_key else 'NOT SET'}")
    print(f"  Featherless API Key: {'✅' if featherless_key else '❌'} ...{featherless_key[-8:] if featherless_key else 'NOT SET'}")
    print(f"  Audio Source: {audio_source}")
    print(f"  Use Mock: {use_mock}")
    
    # Check 2: Audio Capture
    print("\n2️⃣  AUDIO CAPTURE CHECK")
    print("-" * 70)
    
    try:
        from audio_capture import stream_audio_chunks
        print("  ✅ audio_capture module loaded")
        
        # Try to get first chunk with timeout
        print("  Testing audio capture (will timeout after 5s)...")
        chunk_count = 0
        
        try:
            async with asyncio.timeout(5):  # 5 second timeout
                async for chunk in stream_audio_chunks(source=audio_source):
                    chunk_count += 1
                    print(f"    ✅ Chunk {chunk_count}: {chunk.shape} {chunk.dtype}")
                    if chunk_count >= 1:
                        break
        except asyncio.TimeoutError:
            print("    ⏱️  Timeout (this is normal for mic mode)")
        
        if chunk_count > 0:
            print(f"  ✅ Audio capture working ({chunk_count} chunks)")
        else:
            print("  ⚠️  No chunks captured (may need to speak into mic)")
    
    except Exception as e:
        print(f"  ❌ Audio capture failed: {e}")
    
    # Check 3: Transcription
    print("\n3️⃣  TRANSCRIPTION CHECK")
    print("-" * 70)
    
    try:
        from transcriber import transcribe_chunk
        import numpy as np
        
        print("  ✅ transcriber module loaded")
        
        # Create test audio
        test_audio = np.random.randn(16000 * 4).astype(np.float32) * 0.1
        print("  Testing transcription (4 seconds of noise)...")
        
        result = await transcribe_chunk(test_audio, 16000)
        
        print(f"  ✅ Transcription working")
        print(f"    Text: '{result['text'][:50]}...'")
        print(f"    Language: {result['language']}")
        print(f"    Confidence: {result['confidence']:.2%}")
        print(f"    Words: {len(result['words'])}")
    
    except Exception as e:
        print(f"  ❌ Transcription failed: {e}")
    
    # Check 4: Analysis
    print("\n4️⃣  ANALYSIS CHECK")
    print("-" * 70)
    
    try:
        from analyzer import analyze_transcript
        from models import MultimodalTranscript, TranscriptSegment
        
        print("  ✅ analyzer module loaded")
        
        # Create test transcript
        session = MultimodalTranscript()
        session.add_segment(TranscriptSegment(
            time="00:00:05",
            speaker="CALLER",
            text="I've been thinking about this for weeks now. I don't see a way forward."
        ))
        
        print("  Testing analysis...")
        analysis = await analyze_transcript(session)
        
        print(f"  ✅ Analysis working")
        print(f"    Risk Level: {analysis.risk_level}")
        print(f"    Risk Score: {analysis.risk_score}/100")
        print(f"    Confidence: {analysis.confidence}")
    
    except Exception as e:
        print(f"  ❌ Analysis failed: {e}")
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    print("""
If all checks pass:
  ✅ Backend should work
  ✅ Start: python main.py
  ✅ Frontend should receive transcript

If audio capture fails:
  ❌ Check microphone is connected
  ❌ Check microphone permissions
  ❌ Try: python test_mic.py

If transcription fails:
  ❌ Sarvam API may be timing out
  ❌ Check internet connection
  ❌ Try: python check_sarvam_status.py

If analysis fails:
  ❌ Featherless API may be down
  ❌ Check API key
  ❌ Try: python test_analyzer.py
""")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(diagnose())
