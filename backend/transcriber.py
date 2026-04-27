# Real-time speech transcription using Sarvam AI
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

from key_manager import key_manager, get_sarvam_key, report_key_error, report_key_success, KeyStatus
from mock_data import MOCK_TRANSCRIPT

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Sarvam AI configuration
SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"

# Get initial key status
key_status = key_manager.get_status()
if key_status["total_keys"] > 0:
    logger.info(f"Sarvam AI transcriber initialized with {key_status['total_keys']} keys")
    logger.info(f"Current key: {key_status['current_key']}")
else:
    logger.warning("No valid Sarvam API keys found!")
    logger.warning("Add keys to .env file: SARVAM_API_KEY_1, SARVAM_API_KEY_2, SARVAM_API_KEY_3")



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
    audio_chunk: np.ndarray, sample_rate: int = 16000, context: str = "",
    enable_diarization: bool = True, num_speakers: int = 2
) -> dict:
    """
    Transcribe audio chunk to text with word-level timestamps using Sarvam AI.
    Supports speaker diarization to distinguish between speakers.

    Returns:
    {
        "text": "I've been thinking about this for weeks",
        "words": [
            {"word": "I've", "start": 0.0, "end": 0.2, "confidence": 0.95, "speaker": "SPEAKER_00"},
            {"word": "been", "start": 0.2, "end": 0.4, "confidence": 0.98, "speaker": "SPEAKER_00"},
            ...
        ],
        "language": "en",  # or "hi" for Hindi
        "confidence": 0.94,  # average confidence
        "speaker_segments": [
            {"speaker": "SPEAKER_00", "text": "...", "start": 0.0, "end": 2.5},
            {"speaker": "SPEAKER_01", "text": "...", "start": 2.5, "end": 4.0}
        ]
    }

    Args:
        audio_chunk: Audio data as numpy array, dtype float32
        sample_rate: Sample rate in Hz
        context: Previous transcript text for continuity
        enable_diarization: Enable speaker diarization (default: True)
        num_speakers: Expected number of speakers (default: 2)

    Returns:
        dict: Transcription result with text, words, language, confidence, and speaker info
    """
    sarvam_key = get_sarvam_key()
    
    if not sarvam_key:
        logger.error("No valid Sarvam API key available")
        return {
            "text": "",
            "words": [],
            "language": "unknown",
            "confidence": 0.0,
            "speaker_segments": [],
        }
    
    try:
        # Convert numpy array to WAV bytes
        wav_bytes = _numpy_to_wav_bytes(audio_chunk, sample_rate)
        
        # Encode as base64 for API transmission
        audio_b64 = base64.b64encode(wav_bytes).decode('utf-8')
        
        # Call Sarvam API with retry logic
        result = await _call_sarvam_api(audio_b64, context, enable_diarization, num_speakers, sarvam_key)
        return result
        
    except asyncio.TimeoutError:
        logger.error("Sarvam API timeout - returning empty result")
        logger.info("Tip: Check your internet connection or try again later")
        return {
            "text": "",
            "words": [],
            "language": "unknown",
            "confidence": 0.0,
            "speaker_segments": [],
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        return {
            "text": "",
            "words": [],
            "language": "unknown",
            "confidence": 0.0,
            "speaker_segments": [],
        }


async def _call_sarvam_api(audio_b64: str, context: str, enable_diarization: bool = True, 
                          num_speakers: int = 2, sarvam_key: str = "", max_retries: int = 1) -> dict:
    """
    Call Sarvam AI API with minimal retry logic.
    
    Args:
        audio_b64: Base64-encoded WAV audio
        context: Previous transcript text for continuity (ignored for speed)
        enable_diarization: Enable speaker diarization
        num_speakers: Expected number of speakers
        sarvam_key: The API key to use for this call
        max_retries: Maximum number of retry attempts
    
    Returns:
        dict: Parsed transcription result with speaker information
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
                form.add_field('model', 'saaras:v3')
                
                # Diarization parameters
                if enable_diarization:
                    form.add_field('enable_speaker_diarization', 'true')
                    form.add_field('num_speakers', str(num_speakers))
                    logger.info(f"→ Sarvam API call with diarization (num_speakers={num_speakers})...")
                else:
                    logger.info(f"→ Sarvam API call without diarization...")
                
                # Make request with Bearer token
                headers = {
                    "Authorization": f"Bearer {sarvam_key}"
                }
                
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
                        report_key_success()  # Mark this key usage as successful
                        return _parse_sarvam_response(result, enable_diarization)
                    
                    elif resp.status == 429:
                        logger.error("Rate limited (429) - Sarvam API quota exceeded")
                        report_key_error(KeyStatus.RATE_LIMITED, "Rate limit exceeded")
                        raise Exception("Rate limit exceeded")
                    
                    else:
                        error_text = await resp.text()
                        logger.error(f"Sarvam API error {resp.status}: {error_text}")
                        # If diarization fails, retry without it
                        if enable_diarization and "diarization" in error_text.lower():
                            logger.warning("Diarization not supported, retrying without it...")
                            return await _call_sarvam_api(audio_b64, context, False, num_speakers, sarvam_key, max_retries)
                        
                        # Mark key as invalid for other errors
                        report_key_error(KeyStatus.INVALID, f"API error: {resp.status}")
                        raise Exception(f"API error: {resp.status}")
        
        except asyncio.TimeoutError:
            logger.error(f"✗ Sarvam API timeout after 20s")
            report_key_error(KeyStatus.INVALID, "Timeout")
            raise
        
        except Exception as e:
            logger.error(f"Sarvam API call failed: {e}")
            raise
    
    raise Exception("API call failed")


def _parse_sarvam_response(response: dict, enable_diarization: bool = True) -> dict:
    """
    Parse Sarvam AI API response into standard format.
    Supports speaker diarization if enabled.
    
    Expected Sarvam response format:
    {
        "transcript": "I've been thinking about this",
        "language_code": "en-IN",
        "words": [
            {"word": "I've", "start": 0.0, "end": 0.2},
            {"word": "been", "start": 0.2, "end": 0.4},
            ...
        ],
        "speaker_segments": [
            {"speaker": "SPEAKER_00", "text": "I've been thinking", "start": 0.0, "end": 1.5},
            {"speaker": "SPEAKER_01", "text": "about this for weeks", "start": 1.5, "end": 3.0}
        ]
    }
    
    Args:
        response: Raw API response
        enable_diarization: Whether diarization was requested
    
    Returns:
        dict: Parsed transcription with speaker info
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
        word_info = {
            "word": word_data.get("word", ""),
            "start": word_data.get("start", 0.0),
            "end": word_data.get("end", 0.0),
            "confidence": word_data.get("confidence", 0.95)
        }
        # Add speaker label if diarization is enabled and available
        if enable_diarization and "speaker" in word_data:
            word_info["speaker"] = word_data["speaker"]
        words.append(word_info)
    
    # Calculate average confidence
    if words:
        avg_confidence = sum(w["confidence"] for w in words) / len(words)
    else:
        avg_confidence = 0.0
    
    # Parse speaker segments if available
    speaker_segments = []
    if enable_diarization:
        raw_segments = response.get("speaker_segments", [])
        for seg in raw_segments:
            speaker_segments.append({
                "speaker": seg.get("speaker", "UNKNOWN"),
                "text": seg.get("text", ""),
                "start": seg.get("start", 0.0),
                "end": seg.get("end", 0.0)
            })
        
        # If no speaker_segments but words have speaker info, build segments from words
        if not speaker_segments and words and any("speaker" in w for w in words):
            speaker_segments = _build_speaker_segments_from_words(words)
    
    return {
        "text": text,
        "words": words,
        "language": language,
        "confidence": avg_confidence,
        "speaker_segments": speaker_segments,
    }


def _build_speaker_segments_from_words(words: list) -> list:
    """
    Build speaker segments from word-level speaker labels.
    Groups consecutive words by the same speaker.
    
    Args:
        words: List of word dicts with speaker labels
    
    Returns:
        list: Speaker segments with text, start, end
    """
    if not words:
        return []
    
    segments = []
    current_speaker = None
    current_words = []
    current_start = 0.0
    
    for word in words:
        speaker = word.get("speaker", "UNKNOWN")
        
        if current_speaker is None:
            # First word
            current_speaker = speaker
            current_words = [word["word"]]
            current_start = word["start"]
        elif speaker == current_speaker:
            # Same speaker, continue
            current_words.append(word["word"])
        else:
            # Speaker changed, save current segment
            segments.append({
                "speaker": current_speaker,
                "text": " ".join(current_words),
                "start": current_start,
                "end": word["start"]  # End at start of next word
            })
            # Start new segment
            current_speaker = speaker
            current_words = [word["word"]]
            current_start = word["start"]
    
    # Don't forget the last segment
    if current_words:
        segments.append({
            "speaker": current_speaker,
            "text": " ".join(current_words),
            "start": current_start,
            "end": words[-1]["end"]
        })
    
    return segments


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
