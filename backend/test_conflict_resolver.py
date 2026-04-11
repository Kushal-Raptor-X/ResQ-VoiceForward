"""
Test script for the Multi-Agent Conflict Resolution Engine
"""

from conflict_resolver import ConflictResolver
import json


def test_high_risk_scenario():
    """Test scenario with HIGH risk and conflicting signals"""
    print("=" * 80)
    print("TEST 1: HIGH RISK WITH CONFLICTING SIGNALS")
    print("=" * 80)
    
    resolver = ConflictResolver()
    
    test_input = {
        "language_agent": {
            "level": "HIGH",
            "signals": ["I've decided", "final statements"],
            "reasoning": "Finality language detected",
            "confidence": 82
        },
        "emotion_agent": {
            "level": "MEDIUM",
            "signals": ["flat tone"],
            "reasoning": "Low emotional variation",
            "confidence": 65
        },
        "audio_agent": {
            "level": "LOW",
            "signals": ["quiet background"],
            "reasoning": "No distress audio cues",
            "confidence": 70
        },
        "narrative_agent": {
            "level": "HIGH",
            "signals": ["story conclusion pattern"],
            "reasoning": "Narrative reaching endpoint",
            "confidence": 78
        }
    }
    
    result = resolver.resolve(test_input)
    
    print(f"\n📊 FINAL RISK: {result.final_risk}")
    print(f"📈 CONFIDENCE: {result.confidence_summary}")
    print(f"⚠️  UNCERTAINTY: {result.uncertainty}")
    print(f"🎯 WEIGHTED SCORE: {result.weighted_score:.2f} / 4.0")
    
    print(f"\n🗳️  AGENT VOTES:")
    for agent, vote in result.agent_votes.items():
        print(f"   • {agent}: {vote}")
    
    print(f"\n📝 CONTRIBUTING FACTORS:")
    for factor in result.contributing_factors:
        print(f"   • {factor}")
    
    if result.conflicting_signals:
        print(f"\n⚡ CONFLICTING SIGNALS:")
        for signal in result.conflicting_signals:
            print(f"   • {signal}")
    
    print(f"\n💬 EXPLANATION:")
    print(result.explanation)
    print("\n")


def test_critical_scenario():
    """Test scenario with CRITICAL risk"""
    print("=" * 80)
    print("TEST 2: CRITICAL RISK SCENARIO")
    print("=" * 80)
    
    resolver = ConflictResolver()
    
    test_input = {
        "language_agent": {
            "level": "CRITICAL",
            "signals": ["goodbye", "I'm done", "no point anymore"],
            "reasoning": "Multiple farewell and finality phrases",
            "confidence": 95
        },
        "emotion_agent": {
            "level": "HIGH",
            "signals": ["unusual calm", "detached tone"],
            "reasoning": "Calm after distress - resolution indicator",
            "confidence": 88
        },
        "audio_agent": {
            "level": "MEDIUM",
            "signals": ["isolated environment"],
            "reasoning": "No background voices or activity",
            "confidence": 72
        },
        "narrative_agent": {
            "level": "CRITICAL",
            "signals": ["plan disclosure", "timeline mentioned"],
            "reasoning": "Specific plan and timeline indicated",
            "confidence": 92
        }
    }
    
    result = resolver.resolve(test_input)
    
    print(f"\n📊 FINAL RISK: {result.final_risk}")
    print(f"📈 CONFIDENCE: {result.confidence_summary}")
    print(f"⚠️  UNCERTAINTY: {result.uncertainty}")
    print(f"🎯 WEIGHTED SCORE: {result.weighted_score:.2f} / 4.0")
    
    print(f"\n🗳️  AGENT VOTES:")
    for agent, vote in result.agent_votes.items():
        print(f"   • {agent}: {vote}")
    
    print(f"\n💬 EXPLANATION:")
    print(result.explanation)
    print("\n")


def test_low_risk_scenario():
    """Test scenario with LOW risk"""
    print("=" * 80)
    print("TEST 3: LOW RISK SCENARIO")
    print("=" * 80)
    
    resolver = ConflictResolver()
    
    test_input = {
        "language_agent": {
            "level": "LOW",
            "signals": ["feeling down", "tough day"],
            "reasoning": "General distress language, no risk markers",
            "confidence": 75
        },
        "emotion_agent": {
            "level": "LOW",
            "signals": ["sadness present"],
            "reasoning": "Sadness within normal range",
            "confidence": 80
        },
        "audio_agent": {
            "level": "LOW",
            "signals": ["normal background"],
            "reasoning": "No concerning audio patterns",
            "confidence": 85
        },
        "narrative_agent": {
            "level": "LOW",
            "signals": ["seeking support"],
            "reasoning": "Initial disclosure, building rapport",
            "confidence": 78
        }
    }
    
    result = resolver.resolve(test_input)
    
    print(f"\n📊 FINAL RISK: {result.final_risk}")
    print(f"📈 CONFIDENCE: {result.confidence_summary}")
    print(f"⚠️  UNCERTAINTY: {result.uncertainty}")
    print(f"🎯 WEIGHTED SCORE: {result.weighted_score:.2f} / 4.0")
    
    print(f"\n🗳️  AGENT VOTES:")
    for agent, vote in result.agent_votes.items():
        print(f"   • {agent}: {vote}")
    
    print(f"\n💬 EXPLANATION:")
    print(result.explanation)
    print("\n")


def test_json_output():
    """Test JSON serialization for API output"""
    print("=" * 80)
    print("TEST 4: JSON OUTPUT FORMAT")
    print("=" * 80)
    
    resolver = ConflictResolver()
    
    test_input = {
        "language_agent": {
            "level": "HIGH",
            "signals": ["I've decided"],
            "reasoning": "Finality language detected",
            "confidence": 82
        },
        "emotion_agent": {
            "level": "MEDIUM",
            "signals": ["flat tone"],
            "reasoning": "Low emotional variation",
            "confidence": 65
        },
        "audio_agent": {
            "level": "LOW",
            "signals": ["quiet background"],
            "reasoning": "No distress audio cues",
            "confidence": 70
        },
        "narrative_agent": {
            "level": "HIGH",
            "signals": ["conclusion pattern"],
            "reasoning": "Narrative reaching endpoint",
            "confidence": 78
        }
    }
    
    result = resolver.resolve(test_input)
    
    # Convert to dict for JSON serialization
    output = {
        "final_risk": result.final_risk,
        "confidence_summary": result.confidence_summary,
        "uncertainty": result.uncertainty,
        "explanation": result.explanation,
        "contributing_factors": result.contributing_factors,
        "conflicting_signals": result.conflicting_signals,
        "agent_votes": result.agent_votes,
        "weighted_score": result.weighted_score
    }
    
    print("\n📄 JSON OUTPUT:")
    print(json.dumps(output, indent=2))
    print("\n")


if __name__ == "__main__":
    test_high_risk_scenario()
    test_critical_scenario()
    test_low_risk_scenario()
    test_json_output()
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
