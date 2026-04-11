"""
PII scrubbing before any durable storage (Layer 4 / Layer 5).
Heuristic patterns — not a substitute for legal DLP review.
"""

from __future__ import annotations

import re
from typing import Tuple


_EMAIL = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.I,
)
_PHONE_IN = re.compile(
    r"(?:\+91[\s-]?)?(?:0)?[6-9]\d{9}\b|"
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4,}",
)
_AADHAAR_LIKE = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
_CREDIT = re.compile(r"\b(?:\d{4}[\s-]?){3}\d{4}\b")
_URL_WITH_QUERY = re.compile(r"https?://\S+")
_STREET_NUM = re.compile(r"\b\d{1,5}\s+[A-Za-z0-9.'\s]{3,40}(?:street|st\.|road|rd\.|lane|avenue|nagar)\b", re.I)


def privacy_filter(text: str) -> Tuple[str, list[str]]:
    """
    Remove or redact common PII patterns.

    Returns:
        (sanitized_text, list of redaction category labels applied)
    """
    if not text:
        return "", []

    redactions: list[str] = []
    out = text

    def _sub(pattern: re.Pattern, label: str, repl: str) -> None:
        nonlocal out
        if pattern.search(out):
            redactions.append(label)
            out = pattern.sub(repl, out)

    _sub(_EMAIL, "email", "[REDACTED_EMAIL]")
    _sub(_AADHAAR_LIKE, "aadhaar_like", "[REDACTED_ID]")
    _sub(_CREDIT, "payment_card", "[REDACTED_CARD]")
    _sub(_URL_WITH_QUERY, "url", "[REDACTED_URL]")
    _sub(_STREET_NUM, "address", "[REDACTED_ADDRESS]")
    _sub(_PHONE_IN, "phone", "[REDACTED_PHONE]")

    # Collapse excessive whitespace after redactions
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out, redactions
