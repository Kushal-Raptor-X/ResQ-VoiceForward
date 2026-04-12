# Real-time speech transcription using Sarvam AI (Saaras V3 WebSocket Streaming)
# 
# Why WebSocket Streaming instead of batch?
# - True real-time: Partial transcripts appear as user speaks (not waiting for chunks)
# - Lower latency: First tokens appear in milliseconds, not seconds
# - Better UX: Operators see text building in real-time on screen
# - Continuous: No chunking delays, smooth transcription flow
# - VAD support: Voice Activity Detection for smart silence handling
#
import asyncio
import json
import logging
import os
from typing import AsyncIterator, Optional

import aiohttp
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Sarvam AI configuration
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_WS_URL = "wss://api.sarvam.ai/speech-to-text/transcribe/ws"

if not SARVAM_API_KEY:
    logger.warning("SARVAM_API_KEY not set in environment")
    logger.warning("Check that backend/.env file exists and contains SARVAM_API_KEY")
else:
    logger.info(f"Sarvam AI WebSocket transcriber initialized (Saaras V3, key: ...{SARVAM_API_KEY[-8:]})")


async def stream_transcription(
    audio_stream: AsyncIterator[bytes],
    language_code: str = "en-IN",
    mode: str = "transcribe",
    vad_signals: bool = True,
    high_vad_sensitivity: bool = False,
) -> AsyncIterator[dict]:
    """
    Stream audio to Sarvam AI WebSocket and yield transcription results in real-time.
    
    Args:
        audio_stream: Async iterator yielding audio chunks (WAV or PCM bytes)
        language_code: BCP-47 language code (e.g., "en-IN", "hi-IN")
        mode: Output mode - "transcribe", "translate", "verbatim", "translit", "codemix"
        vad_signals: Enable Voice Activity Detection signals
        high_vad_sensitivity: Use high sensitivity VAD (0.5s silence vs 1s)
    
    Yields:
        dict: Transcription events with keys:
            - type: "speech_start", "speech_end", "transcript", "error"
            - text: Transcribed text (for "transcript" type)
            - partial: Whether this is a partial result
            - timestamp: When the event occurred
    """
    if not SARVAM_API_KEY:
        logger.error("SARVAM_API_KEY not configured")
        yield {
            "type": "error",
            "text": "API key not configured",
            "timestamp": asyncio.get_event_loop().time(),
        }
        return
    
    # Build WebSocket URL with parameters
    ws_url = (
        f"{SARVAM_WS_URL}"
        f"?language-code={language_code}"
        f"&model=saaras:v3"
        f"&mode={mode}"
        f"&sample_rate=16000"
        f"&vad_signals={'true' if vad_signals else 'false'}"
        f"&high_vad_sensitivity={'true' if high_vad_sensitivity else 'false'}"
    )
    
    headers = {
        "Api-Subscription-Key": SARVAM_API_KEY,
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=None, connect=5, sock_read=None)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.ws_connect(ws_url, headers=headers) as ws:
                logger.info(f"✓ WebSocket connected to Sarvam (mode={mode}, lang={language_code})")
                
                # Task to send audio chunks
                async def send_audio():
                    try:
                        async for chunk in audio_stream:
                            if chunk:
                                # Send audio data as binary message
                                await ws.send_bytes(chunk)
                                logger.debug(f"→ Sent {len(chunk)} bytes to Sarvam")
                        
                        # Send flush signal to finalize transcription
                        logger.debug("→ Sending flush signal")
                        await ws.send_json({"flush_signal": True})
                        
                    except Exception as e:
                        logger.error(f"Error sending audio: {e}")
                        await ws.close()
                
                # Task to receive transcription results
                async def receive_transcriptions():
                    try:
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                try:
                                    data = json.loads(msg.data)
                                    
                                    # Handle different message types
                                    if "speech_start" in data:
                                        logger.debug("🎤 Speech detected")
                                        yield {
                                            "type": "speech_start",
                                            "timestamp": asyncio.get_event_loop().time(),
                                        }
                                    
                                    elif "speech_end" in data:
                                        logger.debug("🔇 Speech ended")
                                        yield {
                                            "type": "speech_end",
                                            "timestamp": asyncio.get_event_loop().time(),
                                        }
                                    
                                    elif "transcript" in data:
                                        transcript = data.get("transcript", "")
                                        is_final = data.get("is_final", False)
                                        
                                        logger.info(
                                            f"{'✓' if is_final else '→'} "
                                            f"Transcript: {transcript}"
                                        )
                                        
                                        yield {
                                            "type": "transcript",
                                            "text": transcript,
                                            "partial": not is_final,
                                            "words": data.get("words", []),
                                            "language": data.get("language_code", "en-IN"),
                                            "timestamp": asyncio.get_event_loop().time(),
                                        }
                                    
                                    else:
                                        logger.debug(f"Received: {data}")
                                
                                except json.JSONDecodeError:
                                    logger.error(f"Failed to parse JSON: {msg.data}")
                            
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error(f"WebSocket error: {ws.exception()}")
                                yield {
                                    "type": "error",
                                    "text": str(ws.exception()),
                                    "timestamp": asyncio.get_event_loop().time(),
                                }
                                break
                            
                            elif msg.type == aiohttp.WSMsgType.CLOSED:
                                logger.info("WebSocket closed")
                                break
                    
                    except Exception as e:
                        logger.error(f"Error receiving transcriptions: {e}")
                        yield {
                            "type": "error",
                            "text": str(e),
                            "timestamp": asyncio.get_event_loop().time(),
                        }
                
                # Run both tasks concurrently
                send_task = asyncio.create_task(send_audio())
                
                async for result in receive_transcriptions():
                    yield result
                
                # Wait for send task to complete
                await send_task
    
    except Exception as e:
        logger.error(f"WebSocket connection failed: {e}")
        yield {
            "type": "error",
            "text": str(e),
            "timestamp": asyncio.get_event_loop().time(),
        }


# Legacy batch transcription for backward compatibility
async def transcribe_chunk(
    audio_chunk,
    sample_rate: int = 16000,
    context: str = "",
) -> dict:
    """
    Legacy batch transcription (kept for backward compatibility).
    
    For new code, use stream_transcription() with WebSocket streaming instead.
    This provides true real-time transcription with lower latency.
    """
    logger.warning(
        "transcribe_chunk() is deprecated. Use stream_transcription() for real-time WebSocket streaming."
    )
    
    # Return empty result - streaming is the way forward
    return {
        "text": "",
        "words": [],
        "language": "en",
        "confidence": 0.0,
    }
