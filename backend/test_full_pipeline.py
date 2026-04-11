#!/usr/bin/env python3
"""
Full pipeline test: Audio → Transcription → AI Analysis
Tests the complete flow without needing the frontend.
"""
import asyncio
import sounddevice as sd
import numpy as np
import time
import os
from dotenv import load_dotenv

load_dotenv()

from transcriber import transcribe_chunk
from analyzer import analyze_transcript
from models import MultimodalTranscript, TranscriptSegment, ProsodyFeatures, WordTimestamp

SAMPLE_RATE = 16000
CHUNK_DURATION = 4

async def test_full_pipeline():
    print("\n" + "="*70)
    print("  🔬 FULL PIPELINE TEST")
    print("  Audio → Transcription → AI Analysis")
    print("="*70)
    
    # Check API keys
    sarvam_key = os.getenv("SARVAM_API_KEY")
    featherless_key = os.getenv("FEATHERLESS_API_KEY")
    
    if not sarvam_key:
        print("\n❌ SARVAM_API_KEY not found!")
        return
    if not featherless_key:
        print("\n❌ FEATHERLESS_API_KEY not found!")
        return
    
    print(f"\n✅ Sarvam API Key: ...{sarvam_key[-8:]}")
    print(f"✅ Featherless API Key: ...{featherless_key[-8:]}")
    
    # Check microphone
    try:
        default_input = sd.query_devices(kind='input')
        print(f"✅ Microphone: {default_input['name']}")
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return
    
    print("\n" + "="*70)
    print("TEST FLOW:")
    print("  1. Record audio from microphone")
    print("  2. Transcribe with Sarvam AI")
    print("  3. Analyze with Featherless AI (DeepSeek)")
    print("  4. Show risk analysis results")
    print("\n" + "="*70)
    
    input("\n📍 Press ENTER to start (will record 3 chunks)...")
    
    # Initialize session
    session = MultimodalTranscript()
    elapsed_time = 0
    
    print("\n🔴 RECORDING... Speak naturally!\n")
    print("Suggested: 'Hi, I've been feeling really low lately. Work is tough.'")
    print("\n" + "="*70)
    
    for chunk_num in range(1, 4):
        print(f"\n[CHUNK {chunk_num}/3]")
        
        # Step 1: Record audio
        print(f"  🎤 Recording {CHUNK_DURATION}s...")
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
            print("  ⚠️  Silent - skipping")
            continue
        
        print(f"  ✅ Audio captured (level: {max_amp:.3f})")
        
        # Step 2: Transcribe
        print(f"  📡 Transcribing with Sarvam AI...")
        context = session.get_recent_context(seconds=30) if session.segments else ""
        result = await transcribe_chunk(audio, SAMPLE_RATE, context)
        t_transcribe = time.time()
        
        if not result['text']:
            print("  ⚠️  No transcription")
            continue
        
        print(f"  ✅ Transcribed: \"{result['text']}\"")
        print(f"     Language: {result['language']}, Confidence: {result['confidence']:.1%}")
        print(f"     Timing: {t_transcribe - t_record:.2f}s")
        
        # Build segment
        segment = TranscriptSegment(
            time=f"00:00:{elapsed_time:02d}",
            speaker="CALLER" if chunk_num % 2 == 1 else "OPERATOR",
            text=result['text'],
            words=[WordTimestamp(**w) for w in result['words']],
            language=result['language'],
            prosody=ProsodyFeatures(),  # Skip prosody for speed
            ambient={"primary_class": "unknown", "confidence": 0.0, "secondary_classes": [], "risk_relevant": False},
            isRisk=False
        )
        
        session.add_segment(segment)
        elapsed_time += CHUNK_DURATION
        
        print(f"  ✅ Segment added to session")
    
    # Step 3: Analyze with AI
    if not session.segments:
        print("\n❌ No segments to analyze")
        return
    
    print("\n" + "="*70)
    print("📊 ANALYZING WITH AI...")
    print("="*70)
    
    t_analyze_start = time.time()
    analysis = await analyze_transcript(session)
    t_analyze_end = time.time()
    
    # Display results
    print("\n" + "="*70)
    print("✅ AI ANALYSIS COMPLETE")
    print("="*70)
    
    print(f"\n🚨 RISK LEVEL: {analysis.risk_level}")
    print(f"📊 RISK SCORE: {analysis.risk_score}/100")
    print(f"🎯 CONFIDENCE: {analysis.confidence}")
    
    print(f"\n⏱️  ANALYSIS TIME: {t_analyze_end - t_analyze_start:.2f}s")
    
    print("\n🔍 TRIGGERED SIGNALS:")
    for signal in analysis.triggered_signals:
        print(f"  • {signal}")
    
    print("\n🤖 AGENT BREAKDOWN:")
    print(f"  • Language Agent: {analysis.agent_breakdown.language_agent}")
    print(f"  • Emotion Agent: {analysis.agent_breakdown.emotion_agent}")
    print(f"  • Narrative Agent: {analysis.agent_breakdown.narrative_agent}")
    
    if analysis.conflict:
        print(f"\n⚖️  CONFLICT RESOLUTION:")
        print(f"  {analysis.conflict}")
    
    print(f"\n💬 SUGGESTED RESPONSE:")
    print(f"  \"{analysis.suggested_response}\"")
    
    if analysis.operator_note:
        print(f"\n📝 OPERATOR NOTE:")
        print(f"  {analysis.operator_note}")
    
    print("\n" + "="*70)
    print("✅ FULL PIPELINE TEST COMPLETE")
    print("="*70)
    
    print("\n📊 SUMMARY:")
    print(f"  Segments processed: {len(session.segments)}")
    print(f"  Total text: {sum(len(s.text) for s in session.segments)} chars")
    print(f"  Risk level: {analysis.risk_level}")
    print(f"  Risk score: {analysis.risk_score}/100")
    
    print("\n✅ All systems working!")
    print("\nNext: Start the full app:")
    print("  Terminal 1: cd backend && python main.py")
    print("  Terminal 2: cd frontend && npm run dev")
    print("  Browser: http://localhost:5173")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_full_pipeline())
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
