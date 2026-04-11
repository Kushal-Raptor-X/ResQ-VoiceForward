"""Unit tests for Layer 4 (longitudinal) and Layer 5 (audit, privacy, failures)."""

from __future__ import annotations

import time

import pytest

from audit_logger import AuditLogger
from failure_handlers import handle_misclassification_risk, handle_stt_failure
from kiro_config import clear_ethical_config_cache
from longitudinal_store import JsonLongitudinalStore
from pattern_engine import PatternEngine, reset_pattern_engine_singleton
from privacy_filter import privacy_filter


def test_privacy_filter_redacts_email_and_phone():
    raw = "Call me at user@mail.com or +91 9876543210 in Mumbai"
    clean, tags = privacy_filter(raw)
    assert "user@mail.com" not in clean
    assert "9876543210" not in clean
    assert "email" in tags
    assert "phone" in tags


def test_stt_failure_downgrades_when_low_confidence():
    r = handle_stt_failure(0.4, threshold=0.65)
    assert r["stt_reliable"] is False
    assert r["operator_alert"]


def test_misclassification_forces_uncertainty():
    r = handle_misclassification_risk(0.2, True)
    assert r["risk"] == "HIGH"
    assert r["uncertainty_flag"] is True


def test_audit_hash_chain(tmp_path, monkeypatch):
    import audit_logger as al

    logf = tmp_path / "decisions.jsonl"
    monkeypatch.setattr(al, "_audit_path", lambda: logf)
    AuditLogger.reset_for_tests()
    logger = AuditLogger.instance()
    logger.enqueue_decision(
        session_id="sess-a",
        input_text="hello",
        risk="LOW",
        confidence=0.5,
        reasoning={"rule_trigger": None, "ml_score": 0.5},
        operator_action="accepted",
    )
    logger.enqueue_decision(
        session_id="sess-a",
        input_text="world",
        risk="MEDIUM",
        confidence=0.6,
        reasoning={"rule_trigger": None, "ml_score": 0.6},
        operator_action="pending",
    )
    for _ in range(50):
        if logf.is_file() and logf.stat().st_size > 0:
            lines = logf.read_text(encoding="utf-8").strip().splitlines()
            if len(lines) >= 2:
                break
        time.sleep(0.02)
    assert logf.is_file()
    lines = logf.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    rep = logger.verify_chain()
    assert rep["ok"] is True
    replay = logger.replay_call("sess-a")
    assert replay["count"] >= 1
    AuditLogger.reset_for_tests()


def test_pattern_engine_early_risk_and_phrase_stats(tmp_path):
    clear_ethical_config_cache()
    store = JsonLongitudinalStore(tmp_path)
    eng = PatternEngine()
    eng.store = store
    cid = eng.open_call_session("anon-session-1")
    eng.record_risk_tick(cid, 1.0, "HIGH", stt_confidence=0.9)
    eng.record_risk_tick(cid, 3.0, "HIGH", stt_confidence=0.88)
    eng.record_operator_action(cid, "accepted", "I understand how you feel")
    eng.close_call_session(cid, "resolved")

    score = eng.predict_early_risk_score(cid)
    assert "early_risk_score" in score

    phrases = eng.phrase_effectiveness(5)
    assert isinstance(phrases, list)

    insights = eng.build_supervisor_insights()
    assert "top_effective_phrases" in insights
    assert "high_risk_patterns" in insights
    assert "resource_gaps" in insights
    reset_pattern_engine_singleton()
