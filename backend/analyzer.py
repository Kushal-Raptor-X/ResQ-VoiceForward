"""
Orchestrates the 4-agent pipeline and conflict resolution.
Agents run sequentially to respect Featherless single-concurrency limit.
Falls back to mock data if the API is unavailable.
"""
from agents import (
    resolve_conflict,
    run_context_agent,
    run_emotion_agent,
    run_language_agent,
    run_risk_agent,
)
from mock_data import MOCK_ANALYSIS
from schemas import RiskAnalysis


async def analyze_transcript(transcript_text: str) -> RiskAnalysis:
    try:
        # Sequential — Featherless plan allows 1 concurrent DeepSeek-V3 request
        language = await run_language_agent(transcript_text)
        emotion  = await run_emotion_agent(transcript_text)
        risk     = await run_risk_agent(transcript_text)
        context  = await run_context_agent(transcript_text)

        return await resolve_conflict(transcript_text, language, emotion, risk, context)

    except Exception as e:
        print(f"[analyzer] Pipeline failed: {e}. Using mock fallback.")
        return RiskAnalysis.model_validate({
            **MOCK_ANALYSIS,
            "risk_level": "HIGH",
            "risk_score": max(MOCK_ANALYSIS["risk_score"], 80),
            "confidence": "UNCERTAIN",
        })
