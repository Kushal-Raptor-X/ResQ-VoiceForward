"""LLM agent — Sarvam AI (OpenAI-compatible) when configured, else safe local fallback."""

from __future__ import annotations

import os
from typing import Any

import httpx


async def generate(text: str, context: list[Any]) -> str:
    """
    Generate empathetic operator-facing phrasing.
    Set SARVAM_API_KEY (+ optional SARVAM_BASE_URL, SARVAM_MODEL) for live Sarvam calls.
    """
    api_key = os.environ.get("SARVAM_API_KEY", "").strip()
    base = os.environ.get("SARVAM_BASE_URL", "https://api.sarvam.ai/v1").rstrip("/")
    model = os.environ.get("SARVAM_MODEL", "sarvam-m").strip()

    ctx_lines = "\n".join(str(x) for x in (context or [])[-12:])
    system = (
        "You are an AI assistant helping a crisis helpline operator. "
        "Produce one short, empathetic, non-directive suggestion the operator can say or adapt. "
        "Do not diagnose, do not promise outcomes, encourage professional and emergency help when risk is high."
    )
    user = f"Recent context:\n{ctx_lines}\n\nLatest caller line:\n{text}"

    if not api_key:
        return (
            "I'm really sorry you're feeling this way. "
            "Do you want to talk about what's making you feel like this?"
        )

    url = f"{base}/chat/completions"
    payload = {
        "model": model,
        "temperature": 0.35,
        "max_tokens": 220,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        choice = (data.get("choices") or [{}])[0]
        msg = (choice.get("message") or {}).get("content") or ""
        msg = (msg or "").strip()
        if msg:
            return msg
    except Exception:
        pass

    return (
        "I'm really sorry you're feeling this way. "
        "Do you want to talk about what's making you feel like this?"
    )
