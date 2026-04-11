"""
agents/analysis_agent.py — Local risk + emotion analysis.

Uses:
1. Rule-based keyword detection (zero latency)
2. DistilBERT SST-2 for sentiment/emotion (loaded ONCE globally)

Model is loaded at import time — never reloaded per request.
All inference runs under torch.no_grad() for speed.
"""
import re
from typing import Optional

# ---------------------------------------------------------------------------
# Global model — loaded ONCE at startup
# ---------------------------------------------------------------------------
_pipeline = None
_model_load_error: Optional[str] = None


def _load_model():
    global _pipeline, _model_load_error
    try:
        from transformers import pipeline as hf_pipeline
        import torch
        _pipeline = hf_pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1,          # CPU — no GPU required
            truncation=True,
            max_length=128,
        )
        print("[analysis_agent] DistilBERT loaded successfully.")
    except Exception as e:
        _model_load_error = str(e)
        print(f"[analysis_agent] Model load failed: {e} — using rule-based only.")


# Load immediately on import
_load_model()

# ---------------------------------------------------------------------------
# Risk keyword rules
# ---------------------------------------------------------------------------

CRITICAL_KEYWORDS = [
    "kill myself", "suicide", "want to die", "end my life",
    "take my life", "not worth living", "better off dead",
    "end it all", "no reason to live", "final goodbye",
]

HIGH_KEYWORDS = [
    "chest pain", "can't breathe", "heart attack", "stroke",
    "overdose", "bleeding", "unconscious", "emergency",
    "hurt myself", "self harm", "cut myself",
    "giving up", "hopeless", "no way out",
]

MEDIUM_KEYWORDS = [
    "feeling low", "depressed", "anxious", "panic",
    "scared", "alone", "nobody cares", "worthless",
    "can't cope", "overwhelmed", "crying",
]

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def _keyword_risk(text: str) -> tuple[str, list[str]]:
    """Fast rule-based keyword scan. Returns (risk_level, matched_signals)."""
    lower = text.lower()
    signals = []

    for kw in CRITICAL_KEYWORDS:
        if kw in lower:
            signals.append(f"critical keyword: '{kw}'")

    for kw in HIGH_KEYWORDS:
        if kw in lower:
            signals.append(f"high-risk keyword: '{kw}'")

    for kw in MEDIUM_KEYWORDS:
        if kw in lower:
            signals.append(f"distress keyword: '{kw}'")

    if any("critical keyword" in s for s in signals):
        return "CRITICAL", signals
    if any("high-risk keyword" in s for s in signals):
        return "HIGH", signals
    if any("distress keyword" in s for s in signals):
        return "MEDIUM", signals
    return "LOW", signals


def _bert_sentiment(text: str) -> tuple[str, float]:
    """
    Run DistilBERT SST-2 under torch.no_grad().
    Maps NEGATIVE → distress signal, POSITIVE → low risk.
    Returns (label, confidence).
    """
    if _pipeline is None:
        return "UNKNOWN", 0.5

    try:
        import torch
        with torch.no_grad():
            result = _pipeline(text[:512])[0]
        label = result["label"]   # POSITIVE or NEGATIVE
        score = float(result["score"])
        return label, score
    except Exception as e:
        print(f"[analysis_agent] BERT inference error: {e}")
        return "UNKNOWN", 0.5


async def analyze(text: str, session_context: list[str] = None) -> dict:
    """
    Combined analysis: keyword rules + DistilBERT.
    Runs synchronously but is called from async context.
    Returns within ~50 ms on CPU.

    Output:
        {
            "risk": "LOW|MEDIUM|HIGH|CRITICAL",
            "confidence": float,
            "emotion": "distressed|neutral|positive",
            "signals": [...],
            "bert_label": str,
        }
    """
    if not text or not text.strip():
        return {"risk": "LOW", "confidence": 0.0, "emotion": "neutral", "signals": [], "bert_label": "UNKNOWN"}

    # 1. Keyword scan (instant)
    kw_risk, signals = _keyword_risk(text)

    # 2. BERT sentiment
    bert_label, bert_conf = _bert_sentiment(text)

    # 3. Combine — escalate conservatively
    bert_risk = "LOW"
    if bert_label == "NEGATIVE":
        if bert_conf > 0.90:
            bert_risk = "HIGH"
        elif bert_conf > 0.75:
            bert_risk = "MEDIUM"
        else:
            bert_risk = "LOW"

    # Take the higher of keyword vs BERT risk
    final_risk = kw_risk if RISK_ORDER[kw_risk] >= RISK_ORDER[bert_risk] else bert_risk

    # If signals conflict (BERT says positive but keywords say HIGH) → escalate
    if bert_label == "POSITIVE" and RISK_ORDER[kw_risk] >= RISK_ORDER["HIGH"]:
        signals.append("conflict: positive tone with high-risk keywords — escalating")
        final_risk = kw_risk  # trust keywords over sentiment

    emotion = "distressed" if bert_label == "NEGATIVE" else ("positive" if bert_label == "POSITIVE" else "neutral")

    # Confidence: average of bert_conf and keyword certainty
    kw_certainty = 1.0 if signals else 0.3
    confidence = round((bert_conf + kw_certainty) / 2, 3)

    return {
        "risk": final_risk,
        "confidence": confidence,
        "emotion": emotion,
        "signals": signals,
        "bert_label": bert_label,
    }
