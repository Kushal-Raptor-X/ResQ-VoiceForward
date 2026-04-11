"""
Layer 5 explicit failure modes — STT, misclassification, resource APIs.
"""

from __future__ import annotations

from typing import Any, Optional

from audit_logger import append_failure_record
from kiro_config import load_ethical_config


def handle_stt_failure(
    transcription_confidence: Optional[float],
    threshold: Optional[float] = None,
) -> dict[str, Any]:
    cfg = load_ethical_config()
    th = float(threshold if threshold is not None else cfg.get("stt_confidence_threshold", 0.65))
    conf = transcription_confidence if transcription_confidence is not None else 1.0
    unreliable = conf < th
    return {
        "stt_reliable": not unreliable,
        "model_confidence_multiplier": 0.55 if unreliable else 1.0,
        "operator_alert": (
            "Speech unclear — verify manually"
            if unreliable
            else None
        ),
        "flags": ["STT_LOW_CONFIDENCE"] if unreliable else [],
        "transcription_confidence": conf,
        "threshold": th,
    }


def handle_misclassification_risk(
    ml_confidence: float,
    conflicting_signals: bool,
    ml_threshold: Optional[float] = None,
) -> dict[str, Any]:
    cfg = load_ethical_config()
    low_th = float(
        ml_threshold if ml_threshold is not None else cfg.get("ml_low_confidence_threshold", 0.45)
    )
    low_conf = ml_confidence < low_th
    escalate = low_conf or conflicting_signals
    return {
        "risk": "HIGH" if escalate else None,
        "uncertainty": escalate or low_conf,
        "uncertainty_flag": escalate,
        "confidence_ceiling": 0.35 if escalate else 1.0,
        "reason_codes": [
            *(["LOW_ML_CONFIDENCE"] if low_conf else []),
            *(["CONFLICTING_SIGNALS"] if conflicting_signals else []),
        ],
    }


def handle_resource_api_failure(
    error: str,
    *,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    append_failure_record(
        "RESOURCE_API",
        error,
        session_id=session_id,
    )
    cfg = load_ethical_config()
    static_list = cfg.get("static_crisis_resources", [])
    return {
        "fallback": "static_list",
        "resources": static_list,
        "operator_note": "Live resource directory unavailable — showing static crisis contacts.",
    }
