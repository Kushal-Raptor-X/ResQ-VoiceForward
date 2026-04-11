"""
India-oriented consent, disclosure, opt-out, and retention markers (Layer 5).
Session state is in-memory; durable flags go through audit / longitudinal stores.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from kiro_config import load_ethical_config


@dataclass
class SessionComplianceState:
    created_monotonic: float = field(default_factory=time.monotonic)
    ai_disclosure_acknowledged: bool = False
    opt_out_ai_suggestions: bool = False
    first_audio_timestamp: Optional[float] = None

    def mark_audio_started(self) -> None:
        if self.first_audio_timestamp is None:
            self.first_audio_timestamp = time.monotonic()

    def seconds_since_audio_start(self) -> float:
        if self.first_audio_timestamp is None:
            return 0.0
        return time.monotonic() - self.first_audio_timestamp


class ComplianceRegistry:
    _sessions: dict[str, SessionComplianceState] = {}
    _lock = threading.RLock()

    @classmethod
    def get(cls, session_id: str) -> SessionComplianceState:
        with cls._lock:
            if session_id not in cls._sessions:
                cls._sessions[session_id] = SessionComplianceState()
            return cls._sessions[session_id]

    @classmethod
    def acknowledge_ai_disclosure(cls, session_id: str) -> None:
        cls.get(session_id).ai_disclosure_acknowledged = True

    @classmethod
    def set_opt_out(cls, session_id: str, enabled: bool = True) -> None:
        cls.get(session_id).opt_out_ai_suggestions = enabled

    @classmethod
    def should_play_ai_disclosure(cls, session_id: str) -> dict[str, Any]:
        cfg = load_ethical_config()
        window = float(cfg.get("ai_disclosure_window_seconds", 30))
        st = cls.get(session_id)
        st.mark_audio_started()
        elapsed = st.seconds_since_audio_start()
        need = (not st.ai_disclosure_acknowledged) and elapsed <= window
        return {
            "play_ai_disclosure": need,
            "deadline_seconds": max(0.0, window - elapsed),
            "script_hint": (
                "This call uses an AI decision-support assistant for the operator only; "
                "it does not replace human judgment or emergency services."
            ),
        }

    @classmethod
    def ai_suggestions_enabled(cls, session_id: str) -> bool:
        return not cls.get(session_id).opt_out_ai_suggestions

    @classmethod
    def retention_hours(cls) -> float:
        return float(load_ethical_config().get("data_retention_hours", 72))


def build_opt_out_response() -> dict[str, Any]:
    return {
        "ai_suggestions_enabled": False,
        "operator_note": "Caller opted out of AI-assisted phrasing. Standard protocols apply.",
        "call_functional": True,
    }
