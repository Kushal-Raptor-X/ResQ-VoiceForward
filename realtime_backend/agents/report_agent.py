"""
agents/report_agent.py — Live call summary builder.

Updates on every chunk. Maintains a rolling summary per session.
No external calls — pure in-memory aggregation.
"""
from typing import Optional

# Per-session report store
_reports: dict[str, dict] = {}

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

RECOMMENDED_ACTIONS = {
    "LOW": "Continue active listening. No immediate intervention required.",
    "MEDIUM": "Increase engagement. Ask open-ended questions. Monitor closely.",
    "HIGH": "Prepare resource referral. Do not end call. Supervisor awareness recommended.",
    "CRITICAL": "IMMEDIATE ACTION: Do not end call. Notify supervisor. Dispatch emergency if location known.",
}


async def update_report(
    session_id: str,
    text: str,
    risk: str,
    emotion: str,
    signals: list[str],
    resources: Optional[dict] = None,
) -> dict:
    """
    Update the live report for a session.
    Called on every chunk — must be fast.

    Output:
        { "summary": str, "risk": str, "recommended_action": str, "chunk_count": int }
    """
    if session_id not in _reports:
        _reports[session_id] = {
            "summary": "",
            "risk": "LOW",
            "emotion": "neutral",
            "all_signals": [],
            "chunk_count": 0,
            "text_so_far": "",
        }

    report = _reports[session_id]
    report["chunk_count"] += 1
    report["text_so_far"] = (report["text_so_far"] + " " + text).strip()[-500:]  # keep last 500 chars

    # Escalate risk — never downgrade mid-call
    if RISK_ORDER.get(risk, 0) > RISK_ORDER.get(report["risk"], 0):
        report["risk"] = risk

    report["emotion"] = emotion

    # Accumulate unique signals
    for sig in signals:
        if sig not in report["all_signals"]:
            report["all_signals"].append(sig)

    # Build summary
    signal_str = "; ".join(report["all_signals"][:5]) if report["all_signals"] else "none detected"
    report["summary"] = (
        f"Call in progress ({report['chunk_count']} updates). "
        f"Current risk: {report['risk']}. "
        f"Emotion: {report['emotion']}. "
        f"Signals: {signal_str}."
    )

    return {
        "summary": report["summary"],
        "risk": report["risk"],
        "emotion": report["emotion"],
        "recommended_action": RECOMMENDED_ACTIONS.get(report["risk"], RECOMMENDED_ACTIONS["LOW"]),
        "signals": report["all_signals"][:10],
        "chunk_count": report["chunk_count"],
        "resources": resources,
    }


def get_report(session_id: str) -> Optional[dict]:
    return _reports.get(session_id)


def clear_report(session_id: str) -> None:
    _reports.pop(session_id, None)
