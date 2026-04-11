"""Layer 5 — structured transparency envelope on every recommendation."""


def build_recommendation_envelope(
    *,
    risk: str,
    confidence: float,
    explanation: str,
    uncertainty: bool = False,
) -> dict:
    return {
        "risk": risk,
        "confidence": round(float(confidence), 4),
        "explanation": explanation,
        "uncertainty": uncertainty,
    }
