"""Rule-based agent for detecting high-risk mental health indicators."""

HIGH_RISK = [
    "kill myself",
    "suicide",
    "want to die",
    "end my life",
    "no reason to live"
]

def detect(text: str):
    """Detect high-risk phrases in text."""
    text = text.lower()
    for phrase in HIGH_RISK:
        if phrase in text:
            return "CRITICAL"
    return None
