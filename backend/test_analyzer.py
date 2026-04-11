#!/usr/bin/env python3
"""
Test AI analyzer with mock transcript.
Verifies Featherless AI is processing transcripts correctly.
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from analyzer import analyze_transcript
from models import MultimodalTranscript, TranscriptSegment, ProsodyFeatures

async def test_analyzer():
    print("\n" + "="*70)
    print("  🤖 AI ANALYZER TEST")
    print("  Testing Featherless AI (DeepSeek-V3)")
    print("="*70)
    
    # Check API key
    api_key = os.getenv("FEATHERLESS_API_KEY")
    if not api_key:
        print("\n❌ FEATHERLESS_API_KEY not found!")
        print("Check backend/.env file")
        return
    
    print(f"\n✅ API Key: ...{api_key[-8:]}")
    
    # Create mock transcript
    print("\n📝 Creating mock transcript...")
    
    session = MultimodalTranscript()
    
    # Segment 1: LOW risk
    session.add_segment(TranscriptSegment(
        time="00:00:05",
        speaker="CALLER",
        text="Hi, I've been feeling really low lately. Work is tough.",
        language="en",
        prosody=ProsodyFeatures(
            speaking_rate_wpm=140,
            pitch_variance=40.0,
            energy_db=-12.0,
            unusual_calm=False
        ),
        isRisk=False
    ))
    
    # Segment 2: MEDIUM risk
    session.add_segment(TranscriptSegment(
        time="00:00:15",
        speaker="CALLER",
        text="I've been thinking about this for weeks now. I don't see a way forward.",
        language="en",
        prosody=ProsodyFeatures(
            speaking_rate_wpm=100,
            pitch_variance=25.0,
            energy_db=-15.0,
            unusual_calm=False
        ),
        isRisk=False
    ))
    
    # Segment 3: HIGH risk
    session.add_segment(TranscriptSegment(
        time="00:00:25",
        speaker="CALLER",
        text="I think I've finally decided what I need to do. I feel very calm about it.",
        language="en",
        prosody=ProsodyFeatures(
            speaking_rate_wpm=80,
            pitch_variance=15.0,
            energy_db=-18.0,
            unusual_calm=True
        ),
        isRisk=False
    ))
    
    print(f"✅ Created {len(session.segments)} segments")
    
    # Analyze
    print("\n📡 Sending to Featherless AI...")
    print("   (This may take 3-5 seconds)")
    
    import time
    t_start = time.time()
    
    try:
        analysis = await analyze_transcript(session)
        t_end = time.time()
        
        print(f"\n✅ Analysis complete in {t_end - t_start:.2f}s")
        
        # Display results
        print("\n" + "="*70)
        print("📊 ANALYSIS RESULTS")
        print("="*70)
        
        print(f"\n🚨 RISK LEVEL: {analysis.risk_level}")
        print(f"📊 RISK SCORE: {analysis.risk_score}/100")
        print(f"🎯 CONFIDENCE: {analysis.confidence}")
        
        print("\n🔍 TRIGGERED SIGNALS:")
        for i, signal in enumerate(analysis.triggered_signals, 1):
            print(f"  {i}. {signal}")
        
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
        
        # Validation
        print("\n✅ VALIDATION:")
        checks = [
            ("Risk level set", analysis.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
            ("Risk score valid", 0 <= analysis.risk_score <= 100),
            ("Triggered signals present", len(analysis.triggered_signals) > 0),
            ("Agent breakdown present", bool(analysis.agent_breakdown.language_agent)),
            ("Suggested response present", len(analysis.suggested_response) > 0),
        ]
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
        
        all_passed = all(passed for _, passed in checks)
        
        if all_passed:
            print("\n🎉 ALL CHECKS PASSED!")
            print("\nThe AI analyzer is working correctly.")
            print("Ready to test full pipeline with:")
            print("  python test_full_pipeline.py")
        else:
            print("\n⚠️  Some checks failed. Review the output above.")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analyzer())
