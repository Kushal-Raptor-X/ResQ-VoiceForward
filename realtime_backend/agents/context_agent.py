"""
agents/context_agent.py — Session memory window.

Maintains last 5–10 messages per session in-memory.
No external dependencies — pure Python deque.
"""
from collections import deque
from typing import Optional


# Global session store: session_id → deque of message dicts
_sessions: dict[str, deque] = {}

WINDOW_SIZE = 10  # keep last 10 messages


def _get_or_create(session_id: str) -> deque:
    if session_id not in _sessions:
        _sessions[session_id] = deque(maxlen=WINDOW_SIZE)
    return _sessions[session_id]


async def add_message(session_id: str, text: str, role: str = "caller", risk: str = "LOW") -> None:
    """Append a new message to the session window."""
    window = _get_or_create(session_id)
    window.append({"role": role, "text": text, "risk": risk})


async def get_context(session_id: str) -> dict:
    """
    Return the current session context window.

    Output:
        {
            "session_id": str,
            "messages": [...],
            "escalation_trend": "stable|rising|critical",
            "message_count": int,
        }
    """
    window = _get_or_create(session_id)
    messages = list(window)

    # Detect escalation trend from risk levels in window
    risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    risk_values = [risk_order.get(m.get("risk", "LOW"), 0) for m in messages]

    trend = "stable"
    if len(risk_values) >= 2:
        recent = risk_values[-3:]
        if recent[-1] >= 2:
            trend = "critical"
        elif recent[-1] > risk_values[0]:
            trend = "rising"

    return {
        "session_id": session_id,
        "messages": messages,
        "escalation_trend": trend,
        "message_count": len(messages),
    }


async def get_context_text(session_id: str) -> str:
    """Return last N messages as plain text for LLM context."""
    window = _get_or_create(session_id)
    return " | ".join(m["text"] for m in window if m.get("text"))


def clear_session(session_id: str) -> None:
    """Remove session on disconnect."""
    _sessions.pop(session_id, None)


def get_all_sessions() -> list[str]:
    return list(_sessions.keys())
