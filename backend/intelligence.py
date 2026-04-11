"""
Core intelligence pipeline for POST /analyze.
Layers 2, 4, 5 — multi-agent reasoning, learning, ethics.
"""
import uuid
from typing import Optional

from agents import (
    resolve_conflict,
    run_context_agent,
    run_emotion_agent,
    run_language_agent,
    run_risk_agent,
)
from config.db import get_db
from database import get_insights
from logCall import log_call
from mongo_audit import schedule_audit_log
from privacy_filter import privacy_filter
from schemas import AnalyzeInsights, AnalyzeResponse

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

# Numeric confidence mapping for the response
CONFIDENCE_SCORE = {"HIGH": 0.90, "MEDIUM": 0.65, "LOW": 0.40, "UNCERTAIN": 0.25}


async def run_analyze_pipeline(
    transcript: str,
    session_id: Optional[str] = None,
    transcription_confidence: Optional[float] = None,
    elapsed_minutes: float = 0.0,
) -> AnalyzeResponse:
    """
    Full Layer 2 + 4 + 5 pipeline:
    1. Validate input (Layer 5 failure modes)
    2. Run 4 agents in parallel (Layer 2)
    3. Conflict resolution (Layer 2)
    4. Build warnings (Layer 5 transparency)
    5. Fetch insights from MongoDB (Layer 4)
    6. Log to MongoDB (Layer 4)
    7. Return structured response
    """
    session_id = session_id or str(uuid.uuid4())
    warnings: list[str] = []

    # ── Layer 5: Input validation failure modes ──────────────────────────
    if not transcript or not transcript.strip():
        return _empty_transcript_response(session_id)

    if len(transcript.strip()) < 10:
        warnings.append("Transcript too short — confidence is low. Do not rely on this assessment.")

    stt_threshold = 0.65
    stt_reliable = True
    if transcription_confidence is not None:
        stt_reliable = float(transcription_confidence) >= stt_threshold
        if not stt_reliable:
            warnings.append(
                "Speech unclear — verify manually (low transcription confidence). "
                "Model confidence has been downgraded."
            )

    # ── Layer 2: Run all 4 agents sequentially (Featherless 1-concurrency limit) ──
    language = await run_language_agent(transcript)
    emotion  = await run_emotion_agent(transcript)
    risk     = await run_risk_agent(transcript)
    context  = await run_context_agent(transcript)

    # ── Layer 2: Conflict resolution ─────────────────────────────────────
    analysis = await resolve_conflict(transcript, language, emotion, risk, context)

    # ── Layer 5: Build reasoning array (human-readable) ──────────────────
    reasoning = _build_reasoning(language, emotion, risk, context, analysis)

    # ── Layer 5: Uncertainty warnings ────────────────────────────────────
    verdicts = {
        language.get("verdict", "UNCERTAIN"),
        emotion.get("verdict", "UNCERTAIN"),
        risk.get("verdict", "UNCERTAIN"),
        context.get("verdict", "UNCERTAIN"),
    }
    if len(verdicts) > 2:
        warnings.append(
            "Agents disagree significantly — confidence reduced. "
            "Conservative escalation applied per protocol."
        )
    if analysis.confidence == "UNCERTAIN":
        warnings.append(
            "Confidence is UNCERTAIN. Signals are contradictory. "
            "Risk has been escalated to the higher level as a precaution."
        )
    if "UNCERTAIN" in verdicts:
        warnings.append("One or more agents returned UNCERTAIN — partial signal data.")

    if not analysis.triggered_signals:
        warnings.append("No strong signals detected — marking as uncertain. Operator judgment required.")

    db = get_db()
    if db is None:
        warnings.append(
            "MongoDB not connected — analysis runs, but call history is stored in-memory only "
            "until MONGO_URI is set in backend/.env (see .env.example)."
        )

    # ── Layer 4: Fetch insights from MongoDB ─────────────────────────────
    insights_data = await get_insights(analysis.risk_level, analysis.triggered_signals)
    insights = AnalyzeInsights(**insights_data)

    # ── Layer 4: Extract risk phrases ────────────────────────────────────
    from logCall import _RISK_PHRASES  # reuse phrase list
    phrase_tokens = [p for p in _RISK_PHRASES if p in transcript.lower()]

    agent_verdicts = {
        "language": language.get("verdict"),
        "emotion": emotion.get("verdict"),
        "risk": risk.get("verdict"),
        "context": context.get("verdict"),
    }

    conf_val = CONFIDENCE_SCORE.get(analysis.confidence, 0.25)
    if not stt_reliable:
        conf_val = max(0.05, min(conf_val, conf_val * 0.55))

    risk_timeline = [
        {
            "t_minutes": float(elapsed_minutes),
            "risk": analysis.risk_level,
            "stt_confidence": transcription_confidence,
        }
    ]
    transparency = {
        "risk": analysis.risk_level,
        "confidence": conf_val,
        "explanation": "; ".join(reasoning[:4]) if reasoning else "No acute indicators",
        "uncertainty": analysis.confidence == "UNCERTAIN",
    }
    resources_snapshot = [r.model_dump() for r in analysis.resources]

    # ── Layer 4: Log to MongoDB via logCall() (privacy-filtered transcript) ─
    record_id = await log_call(
        db=db,
        session_id=session_id,
        transcript=transcript,
        phrases=phrase_tokens,
        risk_level=analysis.risk_level,
        confidence=conf_val,
        reasoning=reasoning,
        agent_verdicts=agent_verdicts,
        triggered_signals=analysis.triggered_signals,
        suggested_response=analysis.suggested_response,
        operator_action="pending",
        risk_timeline=risk_timeline,
        stt_confidence=transcription_confidence,
        stt_reliable=stt_reliable,
        transparency=transparency,
        resources_snapshot=resources_snapshot,
    )

    redacted_for_audit, _reds = privacy_filter(transcript)
    schedule_audit_log(
        db,
        session_id=session_id,
        record_id=record_id,
        input_text=redacted_for_audit,
        risk=analysis.risk_level,
        confidence=conf_val,
        reasoning={
            "agent_verdicts": agent_verdicts,
            "conflict": analysis.conflict,
            "risk_score": analysis.risk_score,
        },
        transparency=transparency,
        operator_action="pending",
        stt_reliable=stt_reliable,
        privacy_redactions=_reds,
    )

    # ── Build response ────────────────────────────────────────────────────
    return AnalyzeResponse(
        session_id=session_id,
        risk=analysis.risk_level,
        risk_score=analysis.risk_score,
        confidence=conf_val,
        confidence_label=analysis.confidence,
        reasoning=reasoning,
        triggered_signals=analysis.triggered_signals,
        agent_breakdown={
            "language_agent": {"verdict": language.get("verdict"), "reasoning": language.get("reasoning"), "signals": language.get("signals", [])},
            "emotion_agent":  {"verdict": emotion.get("verdict"),  "reasoning": emotion.get("reasoning"),  "signals": emotion.get("signals", [])},
            "risk_agent":     {"verdict": risk.get("verdict"),     "reasoning": risk.get("reasoning"),     "signals": risk.get("signals", [])},
            "context_agent":  {"verdict": context.get("verdict"),  "reasoning": context.get("reasoning"),  "signals": context.get("signals", [])},
        },
        conflict=analysis.conflict,
        conflict_resolution=analysis.conflict_resolution,
        suggested_response=analysis.suggested_response,
        operator_note=analysis.operator_note,
        resources=[r.model_dump() for r in analysis.resources],
        insights=insights,
        warnings=warnings,
        record_id=record_id,
    )


def _build_reasoning(language: dict, emotion: dict, risk: dict, context: dict, analysis) -> list[str]:
    """Build a human-readable reasoning array from all agent outputs."""
    lines = []

    # Agent signals → reasoning sentences
    for sig in language.get("signals", []):
        lines.append(f"Phrase detected: '{sig}'")
    for sig in emotion.get("signals", []):
        lines.append(f"Emotion signal: {sig}")
    for sig in risk.get("signals", []):
        lines.append(f"Risk indicator: {sig}")
    for sig in context.get("signals", []):
        lines.append(f"Context pattern: {sig}")

    # Agent verdicts
    lines.append(
        f"Language Agent → {language.get('verdict', 'UNCERTAIN')}: {language.get('reasoning', '')}"
    )
    lines.append(
        f"Emotion Agent → {emotion.get('verdict', 'UNCERTAIN')}: {emotion.get('reasoning', '')}"
    )
    lines.append(
        f"Risk Agent → {risk.get('verdict', 'UNCERTAIN')}: {risk.get('reasoning', '')}"
    )
    lines.append(
        f"Context Agent → {context.get('verdict', 'UNCERTAIN')}: {context.get('reasoning', '')}"
    )

    # Conflict resolution
    if analysis.conflict:
        lines.append(f"Conflict: {analysis.conflict}")
    if analysis.conflict_resolution:
        lines.append(f"Resolution: {analysis.conflict_resolution}")

    return [l for l in lines if l.strip()]


def _empty_transcript_response(session_id: str) -> AnalyzeResponse:
    """Layer 5: Specific failure mode for empty/missing transcript."""
    return AnalyzeResponse(
        session_id=session_id,
        risk="LOW",
        risk_score=0,
        confidence=0.0,
        confidence_label="UNCERTAIN",
        reasoning=["No transcript provided — cannot assess risk."],
        triggered_signals=[],
        agent_breakdown={},
        conflict="",
        conflict_resolution="",
        suggested_response="",
        operator_note="",
        resources=[],
        insights=AnalyzeInsights(
            similar_case_risk="unavailable",
            best_response_success="unavailable",
            data_note="No transcript to analyse.",
        ),
        warnings=[
            "EMPTY TRANSCRIPT — no analysis performed.",
            "Low confidence warning: transcript is empty or unclear.",
            "Operator must assess independently.",
        ],
        record_id=None,
    )
