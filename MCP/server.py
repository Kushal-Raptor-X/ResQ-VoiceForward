"""Production-ready MCP server for mental health risk assessment and support.

Layers 4–5: longitudinal pattern intelligence, ethical audit trail, failure modes,
India compliance hooks, and Sarvam-ready LLM suggestions.
"""

from __future__ import annotations

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from agents import context_agent, decision_agent, llm_agent, ml_agent, rule_agent
from audit_logger import AuditLogger, append_failure_record
from compliance_india import ComplianceRegistry
from failure_handlers import (
    handle_misclassification_risk,
    handle_resource_api_failure,
    handle_stt_failure,
)
from pattern_engine import get_pattern_engine
from transparency import build_recommendation_envelope

mcp = FastMCP("mental-health-mcp")


def _maybe_downgrade_confidence(base: float, stt_state: dict) -> float:
    mult = float(stt_state.get("model_confidence_multiplier") or 1.0)
    return max(0.05, min(0.99, base * mult))


@mcp.tool()
async def analyze_text(
    text: str,
    session_id: str,
    transcription_confidence: Optional[float] = None,
) -> dict:
    """
    Real-time hybrid analysis with Layer 5 failure handling and transparency envelope.
    """
    stt_state = handle_stt_failure(transcription_confidence)
    if not stt_state["stt_reliable"]:
        append_failure_record(
            "STT",
            "Low transcription confidence",
            session_id=session_id,
            extra={"confidence": transcription_confidence},
        )

    context_agent.update(session_id, text)
    context = context_agent.get(session_id)

    rule = rule_agent.detect(text)
    ml = ml_agent.classify(text)

    ml_conf = float(ml["confidence"])
    conflicting = (rule == "CRITICAL" and ml_conf < 0.35) or (
        rule is None and ml_conf < 0.42 and any(
            w in text.lower() for w in ("hurt", "die", "end", "hopeless", "alone")
        )
    )
    mis = handle_misclassification_risk(ml_conf, conflicting)

    decision = decision_agent.decide(rule, ml, context)
    risk = decision["risk"]
    if mis.get("risk") == "HIGH":
        risk = "HIGH"

    base_conf = float(ml["confidence"])
    conf = _maybe_downgrade_confidence(base_conf, stt_state)
    if mis.get("uncertainty"):
        conf = min(conf, float(mis.get("confidence_ceiling") or 0.35))

    reasoning = {
        "rule_trigger": rule,
        "ml_score": ml["confidence"],
        "ml_label": ml.get("label"),
        "misclassification_flags": mis.get("reason_codes", []),
        "stt_flags": stt_state.get("flags", []),
    }

    explanation_parts = []
    if rule:
        explanation_parts.append("Rule-based critical phrase match")
    if float(ml["confidence"]) > 0.7:
        explanation_parts.append("Model indicates strong affective load")
    if conflicting:
        explanation_parts.append("Conflicting signals — conservative HIGH applied")
    if not stt_state["stt_reliable"]:
        explanation_parts.append("Low STT confidence — verify wording manually")
    if not explanation_parts:
        explanation_parts.append("No acute rule triggers; blended model/context assessment")

    envelope = build_recommendation_envelope(
        risk=risk,
        confidence=conf,
        explanation="; ".join(explanation_parts),
        uncertainty=bool(mis.get("uncertainty_flag")),
    )

    AuditLogger.instance().enqueue_decision(
        session_id=session_id,
        input_text=text,
        risk=risk,
        confidence=conf,
        reasoning=reasoning,
        operator_action="pending",
    )

    return {
        "text": text,
        "risk": risk,
        "confidence": conf,
        "context": context,
        "call_llm": decision["call_llm"],
        "stt": stt_state,
        "misclassification_guard": mis,
        "transparency": envelope,
    }


@mcp.tool()
async def generate_suggestion(text: str, session_id: str) -> dict:
    if not ComplianceRegistry.ai_suggestions_enabled(session_id):
        return {
            "suggestion": "",
            "blocked": True,
            "reason": "opt_out",
        }
    context = context_agent.get(session_id)
    response = await llm_agent.generate(text, context)
    return {"suggestion": response}


@mcp.tool()
async def explain_risk(text: str) -> dict:
    rule = rule_agent.detect(text)
    ml = ml_agent.classify(text)
    reason = (
        "High emotional distress detected"
        if rule or float(ml["confidence"]) > 0.7
        else "Low risk indicators"
    )
    return {
        "rule_triggered": rule,
        "model_confidence": ml["confidence"],
        "model_label": ml["label"],
        "reason": reason,
    }


@mcp.tool()
def get_context(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "context": context_agent.get(session_id),
    }


@mcp.tool()
def log_decision(
    session_id: str,
    input_text: str,
    risk: str,
    confidence: float,
    reasoning: dict[str, Any],
    operator_action: str = "pending",
) -> dict:
    """
    Explicitly log one AI decision (privacy-filtered text, hash-chained audit file).
    """
    return AuditLogger.instance().enqueue_decision(
        session_id=session_id,
        input_text=input_text,
        risk=risk,
        confidence=confidence,
        reasoning=reasoning,
        operator_action=operator_action,
    )


@mcp.tool()
def replay_call(session_id: str) -> dict:
    """Immutable audit timeline for a session (inputs + AI decisions + operator flags)."""
    return AuditLogger.instance().replay_call(session_id)


@mcp.tool()
def get_system_insights() -> dict:
    """
    Supervisor dashboard — phrase effectiveness, high-risk longitudinal clusters, resource gaps.
    """
    return get_pattern_engine().build_supervisor_insights()


@mcp.tool()
def report_failure(
    failure_type: str,
    detail: str,
    session_id: Optional[str] = None,
) -> dict:
    """Structured failure reporting (resource API, STT, model, etc.)."""
    return append_failure_record(failure_type, detail, session_id=session_id)


@mcp.tool()
def compliance_status(session_id: str) -> dict:
    """India disclosure window + opt-out + retention policy snapshot."""
    disc = ComplianceRegistry.should_play_ai_disclosure(session_id)
    return {
        "session_id": session_id,
        "ai_disclosure": disc,
        "ai_suggestions_enabled": ComplianceRegistry.ai_suggestions_enabled(session_id),
        "retention_hours": ComplianceRegistry.retention_hours(),
    }


@mcp.tool()
def set_compliance_flags(
    session_id: str,
    acknowledge_ai_disclosure: bool = False,
    opt_out_ai: bool = False,
) -> dict:
    if acknowledge_ai_disclosure:
        ComplianceRegistry.acknowledge_ai_disclosure(session_id)
    if opt_out_ai:
        ComplianceRegistry.set_opt_out(session_id, True)
    return compliance_status(session_id)


@mcp.tool()
def crisis_resources_fallback(session_id: Optional[str] = None) -> dict:
    """Use when external resource APIs fail — logs failure and returns static India helplines."""
    return handle_resource_api_failure("manual tool invocation", session_id=session_id)


@mcp.tool()
def verify_audit_chain() -> dict:
    """Tamper-check the append-only audit log."""
    return AuditLogger.instance().verify_chain()


@mcp.tool()
def run_pattern_learning_batch() -> dict:
    """Offline job hook — train early-risk model and refresh aggregates."""
    return get_pattern_engine().run_offline_batch_learning()


if __name__ == "__main__":
    mcp.run()
