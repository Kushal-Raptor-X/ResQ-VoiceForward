# Real-time speech transcription using Sarvam AI (Saaras V3)
# 
# Why Saaras V3?
# - Streaming support: Lower latency, first tokens appear faster (critical for real-time)
# - Better accuracy: 19% WER vs 22% WER in V2.5
# - Code-mixing: Handles Hindi-English mixing naturally (common in Indian calls)
# - Noise handling: Robust to background noise in call centers
# - 22 Indian languages + English support
#
import asyncio
import base64
import io
import logging
import os
import time
from typing import Optional

import aiohttp
import numpy as np
import scipy.io.wavfile
from dotenv import load_dotenv

from mock_data import MOCK_TRANSCRIPT

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Sarvam AI configuration
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"

if not SARVAM_API_KEY:
    logger.warning("SARVAM_API_KEY not set in environment")
    logger.warning("Check that backend/.env file exists and contains SARVAM_API_KEY")
else:
    logger.info(f"Sarvam AI transcriber initialized (Saaras V3, key: ...{SARVAM_API_KEY[-8:]})")



def _numpy_to_wav_bytes(audio_chunk: np.ndarray, sample_rate: int) -> bytes:
    """Convert numpy array to WAV format bytes."""
    # Ensure float32 and normalize to int16 range
    if audio_chunk.dtype != np.float32:
        audio_chunk = audio_chunk.astype(np.float32)
    
    # Convert float32 [-1, 1] to int16 [-32768, 32767]
    audio_int16 = (audio_chunk * 32767).astype(np.int16)
    
    # Write to bytes buffer
    buffer = io.BytesIO()
    scipy.io.wavfile.write(buffer, sample_rate, audio_int16)
    buffer.seek(0)
    return buffer.read()


async def transcribe_chunk(
    audio_chunk: np.ndarray, sample_rate: int = 16000, context: str = ""
) -> dict:
    """
    Transcribe audio chunk to text with word-level timestamps using Sarvam AI.

    Returns:
    {
        "text": "I've been thinking about this for weeks",
        "words": [
            {"word": "I've", "start": 0.0, "end": 0.2, "confidence": 0.95},
            {"word": "been", "start": 0.2, "end": 0.4, "confidence": 0.98},
            ...
        ],
        "language": "en",  # or "hi" for Hindi
        "confidence": 0.94  # average confidence
    }

    Args:
        audio_chunk: Audio data as numpy array, dtype float32
        sample_rate: Sample rate in Hz
        context: Previous transcript text for continuity

    Returns:
        dict: Transcription result with text, words, language, confidence
    """
    if not SARVAM_API_KEY:
        logger.error("SARVAM_API_KEY not configured")
        return {
            "text": "",
            "words": [],
            "language": "unknown",
            "confidence": 0.0,
        }
    
    try:
        # Convert numpy array to WAV bytes
        wav_bytes = _numpy_to_wav_bytes(audio_chunk, sample_rate)
        
        # Encode as base64 for API transmission
        audio_b64 = base64.b64encode(wav_bytes).decode('utf-8')
        
        # Call Sarvam API with retry logic
        result = await _call_sarvam_api(audio_b64, context)
        return result
        
    except asyncio.TimeoutError:
        logger.error("Sarvam API timeout - returning empty result")
        logger.info("Tip: Check your internet connection or try again later")
        return {
            "text": "",
            "words": [],
            "language": "unknown",
            "confidence": 0.0,
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        return {
            "text": "",
            "words": [],
            "language": "unknown",
            "confidence": 0.0,
        }


async def _call_sarvam_api(audio_b64: str, context: str, max_retries: int = 1) -> dict:  # Only 1 attempt - fail fast
    """
    Call Sarvam AI API with minimal retry logic.
    
    Args:
        audio_b64: Base64-encoded WAV audio
        context: Previous transcript text for continuity (ignored for speed)
        max_retries: Maximum number of retry attempts
    
    Returns:
        dict: Parsed transcription result
    """
    for attempt in range(max_retries):
        try:
            # Aggressive timeout - fail fast if API is slow
            timeout = aiohttp.ClientTimeout(total=20, connect=3, sock_read=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Create form data
                form = aiohttp.FormData()
                
                # Decode base64 back to bytes for file upload
                audio_bytes = base64.b64decode(audio_b64)
                
                # Add audio file
                form.add_field(
                    'file',
                    audio_bytes,
                    filename='audio.wav',
                    content_type='audio/wav'
                )
                
                # Minimal parameters for speed
                form.add_field('language_code', 'en')
                form.add_field('model', 'saaras:v3')  # V3: streaming support, 19% WER, better code-mixing
                
                # Make request with Bearer token
                headers = {
                    "Authorization": f"Bearer {SARVAM_API_KEY}"
                }
                
                logger.info(f"→ Sarvam API call (timeout=20s)...")
                t_start = time.time()
                
                async with session.post(
                    SARVAM_API_URL,
                    data=form,
                    headers=headers
                ) as resp:
                    t_elapsed = time.time() - t_start
                    
                    if resp.status == 200:
                        result = await resp.json()
                        logger.info(f"✓ Sarvam API responded in {t_elapsed:.2f}s")
                        return _parse_sarvam_response(result)
                    
                    elif resp.status == 429:
                        logger.error("Rate limited (429) - Sarvam API quota exceeded")
                        raise Exception("Rate limit exceeded")
                    
                    else:
                        error_text = await resp.text()
                        logger.error(f"Sarvam API error {resp.status}: {error_text}")
                        raise Exception(f"API error: {resp.status}")
        
        except asyncio.TimeoutError:
            logger.error(f"✗ Sarvam API timeout after 20s")
            raise
        
        except Exception as e:
            logger.error(f"Sarvam API call failed: {e}")
            raise
    
    raise Exception("API call failed")


def _parse_sarvam_response(response: dict) -> dict:
    """
    Parse Sarvam AI API response into standard format.
    
    Expected Sarvam response format:
    {
        "transcript": "I've been thinking about this",
        "language_code": "en-IN",
        "words": [
            {"word": "I've", "start": 0.0, "end": 0.2},
            {"word": "been", "start": 0.2, "end": 0.4},
            ...
        ]
    }
    """
    # Log the full response for debugging
    logger.debug(f"Sarvam API response: {response}")
    
    text = response.get("transcript", "").strip()
    
    # Extract language code (e.g., "en-IN" -> "en", "hi-IN" -> "hi")
    language_code = response.get("language_code", "unknown")
    if language_code.startswith("en"):
        language = "en"
    elif language_code.startswith("hi"):
        language = "hi"
    else:
        language = "en"  # Default to English
    
    # Parse word-level timestamps
    words = []
    raw_words = response.get("words", [])
    
    for word_data in raw_words:
        words.append({
            "word": word_data.get("word", ""),
            "start": word_data.get("start", 0.0),
            "end": word_data.get("end", 0.0),
            "confidence": word_data.get("confidence", 0.95)  # Sarvam may not provide confidence
        })
    
    # Calculate average confidence
    if words:
        avg_confidence = sum(w["confidence"] for w in words) / len(words)
    else:
        avg_confidence = 0.0
    
    return {
        "text": text,
        "words": words,
        "language": language,
        "confidence": avg_confidence,
    }


# Keep mock transcription for backward compatibility
async def start_mock_transcription(emit_callback):
    from models import TranscriptSegment
    
    call_start_time = None
    
    for line in MOCK_TRANSCRIPT:
        # Parse time string "00:00:10" to seconds
        time_parts = line["time"].split(":")
        target_time = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
        
        # On first iteration, set start time
        if call_start_time is None:
            call_start_time = asyncio.get_event_loop().time()
        
        # Wait until the target time
        elapsed = asyncio.get_event_loop().time() - call_start_time
        wait_time = target_time - elapsed
        
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        
        # Emit the segment
        segment = TranscriptSegment(
            time=line["time"],
            speaker=line["speaker"],
            text=line["text"],
            isRisk=line["isRisk"],
        )
        await emit_callback(segment)
