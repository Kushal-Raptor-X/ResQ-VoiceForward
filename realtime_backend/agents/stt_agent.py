"""
agents/stt_agent.py — Sarvam AI STT agent.

Processes 300–700 ms audio chunks via Sarvam's speech-to-text API.
Each chunk is dispatched independently — no waiting for previous chunks.
Returns partial text immediately for pipeline consumption.
"""
import asyncio
import hashlib
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

from utils.cache import stt_cache

load_dotenv()

SARVAM_STT_URL = os.getenv("SARVAM_STT_URL", "https://api.sarvam.ai/speech-to-text")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
STT_TIMEOUT = 0.7  # 700 ms hard timeout — never block pipeline


async def transcribe_chunk(
    audio_bytes: bytes,
    language_code: str = "hi-IN",
    sample_rate: int = 16000,
) -> dict:
    """
    Send a single audio chunk to Sarvam STT.
    Non-blocking — uses asyncio timeout so pipeline never stalls.

    Returns:
        { "text": str, "confidence": float, "reliable": bool }
    """
    # Cache check — avoid duplicate API calls for identical chunks
    chunk_hash = hashlib.md5(audio_bytes).hexdigest()
    cached = stt_cache.get(chunk_hash)
    if cached:
        return cached

    result = {"text": "", "confidence": 0.0, "reliable": False}

    try:
        async with httpx.AsyncClient(timeout=STT_TIMEOUT) as client:
            response = await client.post(
                SARVAM_STT_URL,
                headers={
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type": "audio/wav",
                },
                content=audio_bytes,
                params={
                    "language_code": language_code,
                    "model": "saarika:v2",
                    "with_timestamps": "false",
                },
            )
            if response.status_code == 200:
                data = response.json()
                text = data.get("transcript", "")
                confidence = float(data.get("confidence", 0.8))
                result = {
                    "text": text,
                    "confidence": confidence,
                    "reliable": confidence >= 0.6 and len(text.strip()) > 0,
                }
                stt_cache.set(chunk_hash, result)
            else:
                result["text"] = ""
                result["confidence"] = 0.0
                result["reliable"] = False

    except (httpx.TimeoutException, httpx.ConnectError):
        # Timeout — return empty, mark unreliable, never block
        result = {"text": "", "confidence": 0.0, "reliable": False}
    except Exception as e:
        print(f"[stt_agent] Error: {e}")
        result = {"text": "", "confidence": 0.0, "reliable": False}

    return result


async def transcribe_text_mock(text: str) -> dict:
    """
    Mock STT for text input (demo/testing without audio).
    Simulates the same output shape as transcribe_chunk.
    """
    await asyncio.sleep(0.01)  # simulate minimal latency
    return {"text": text, "confidence": 1.0, "reliable": True}
