"""
agents/llm_agent.py — Sarvam AI LLM suggestion agent.

ASYNC ONLY — triggered only when risk >= HIGH.
Never blocks the main pipeline.
Generates: 1 empathetic response + 1 follow-up question.
"""
import asyncio
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

SARVAM_LLM_URL = os.getenv("SARVAM_LLM_URL", "https://api.sarvam.ai/v1/chat/completions")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_LLM_MODEL = os.getenv("SARVAM_LLM_MODEL", "sarvam-2b")
LLM_TIMEOUT = 5.0  # 5s — async background task, not in critical path

SYSTEM_PROMPT = """You are a compassionate crisis helpline assistant supporting a human operator.
Given a caller's transcript, generate:
1. One short empathetic response the operator can say (max 2 sentences, warm and non-clinical)
2. One follow-up question to keep the caller engaged

Respond in JSON only:
{"empathetic_response": "...", "follow_up_question": "..."}
No markdown. No preamble."""


async def generate_suggestion(text: str, context: str = "", risk: str = "HIGH") -> dict:
    """
    Call Sarvam LLM to generate operator suggestion.
    Called as a background task — result sent to frontend when ready.

    Returns:
        { "empathetic_response": str, "follow_up_question": str, "model": str }
    """
    fallback = {
        "empathetic_response": "I hear you, and I'm here with you right now. You're not alone.",
        "follow_up_question": "Can you tell me a little more about what's happening for you today?",
        "model": "fallback",
    }

    if not SARVAM_API_KEY or SARVAM_API_KEY == "your_sarvam_api_key_here":
        return {**fallback, "model": "fallback (no API key)"}

    user_content = f"Caller transcript: {text}"
    if context:
        user_content += f"\nPrevious context: {context}"
    user_content += f"\nCurrent risk level: {risk}"

    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            resp = await client.post(
                SARVAM_LLM_URL,
                headers={
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "model": SARVAM_LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    "max_tokens": 200,
                    "temperature": 0.4,
                },
            )
            if resp.status_code == 200:
                import json, re
                content = resp.json()["choices"][0]["message"]["content"]
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    return {
                        "empathetic_response": parsed.get("empathetic_response", fallback["empathetic_response"]),
                        "follow_up_question": parsed.get("follow_up_question", fallback["follow_up_question"]),
                        "model": SARVAM_LLM_MODEL,
                    }
    except Exception as e:
        print(f"[llm_agent] Sarvam LLM error: {e}")

    return fallback
