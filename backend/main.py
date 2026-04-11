import asyncio
import logging
import os
import time

import socketio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ambient_classifier import classify_ambient_audio
from analyzer import analyze_transcript
from audio_capture import stream_audio_chunks
from models import MultimodalTranscript, ProsodyFeatures, TranscriptSegment, WordTimestamp
from prosody_analyzer import extract_prosody_features
from transcriber import start_mock_transcription, transcribe_chunk

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

fastapi_app = FastAPI()
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve demo audio file
fastapi_app.mount("/demo_audio", StaticFiles(directory="demo_audio"), name="demo_audio")

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=ALLOWED_ORIGINS)
app = socketio.ASGIApp(sio, fastapi_app)
client_tasks: dict[str, list[asyncio.Task]] = {}
call_sessions: dict[str, MultimodalTranscript] = {}


@fastapi_app.get("/health")
async def health():
    return {"status": "ok", "timestamp": int(time.time())}


def format_timestamp(elapsed_sec: float) -> str:
    """Format elapsed seconds as HH:MM:SS."""
    hours = int(elapsed_sec // 3600)
    minutes = int((elapsed_sec % 3600) // 60)
    seconds = int(elapsed_sec % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


async def emit_analysis_loop(sid: str):
    """
    Continuously analyze the multimodal transcript and emit real-time risk analysis.
    Uses Featherless AI (DeepSeek-V3) for fast, accurate analysis.
    """
    logger.info(f"Starting REAL AI analysis loop for session {sid}")
    
    # Wait for some transcript data to accumulate
    await asyncio.sleep(10)
    
    while True:
        try:
            # Get current session
            session = call_sessions.get(sid)
            if not session or len(session.segments) == 0:
                logger.debug(f"No transcript data yet for session {sid}, waiting...")
                await asyncio.sleep(5)
                continue
            
            # Run real AI analysis
            logger.info(f"Running AI analysis on {len(session.segments)} segments...")
            t_start = time.time()
            
            analysis = await analyze_transcript(session)
            
            t_elapsed = time.time() - t_start
            logger.info(f"✓ AI analysis complete in {t_elapsed:.2f}s - Risk: {analysis.risk_level} ({analysis.risk_score}/100)")
            
            # Emit to frontend
            await sio.emit("analysis_update", analysis.model_dump(), to=sid)
            
            # Analyze every 4 seconds for responsive real-time demo
            # (Safe with DeepSeek-V3 typical 3-5s response time)
            await asyncio.sleep(4)
            
        except Exception as e:
            logger.error(f"Analysis loop error: {e}", exc_info=True)
            await asyncio.sleep(10)


async def emit_transcript_loop(sid: str):
    """
    Real audio pipeline: capture → transcribe → extract features → emit.
    Sequential processing with backpressure to prevent queue overflow.
    """
    audio_source = os.getenv("AUDIO_SOURCE", "mic")
    call_start_time = time.time()

    logger.info(f"Starting audio pipeline for session {sid} with source: {audio_source}")

    # Initialize session
    call_sessions[sid] = MultimodalTranscript()

    try:
        chunk_count = 0
        async for audio_chunk in stream_audio_chunks(source=audio_source):
            chunk_count += 1
            elapsed = time.time() - call_start_time
            t_start = time.time()

            logger.info(f"[Chunk {chunk_count}] Processing 8s audio chunk...")

            # Get context for transcription continuity
            context = call_sessions[sid].get_recent_context(seconds=30)

            # Transcribe audio chunk (this will take 15-30s)
            logger.info(f"[Chunk {chunk_count}] → Calling Sarvam AI...")
            transcript_data = await transcribe_chunk(audio_chunk, context=context)
            t_transcribe = time.time()

            logger.info(
                f"[Chunk {chunk_count}] ✓ Transcription: '{transcript_data['text'][:80]}...' "
                f"(lang: {transcript_data['language']}, took {t_transcribe-t_start:.2f}s)"
            )

            # Skip if no speech detected
            if not transcript_data["text"].strip():
                logger.debug(f"[Chunk {chunk_count}] No speech detected, skipping")
                continue

            # Skip prosody extraction for speed (use defaults)
            prosody = ProsodyFeatures().model_dump()

            # Skip ambient classification for speed (use defaults)
            ambient = {"primary_class": "unknown", "confidence": 0.0, "secondary_classes": [], "risk_relevant": False}

            # Determine speaker based on alternating pattern
            # In production, use speaker diarization
            num_segments = len(call_sessions[sid].segments)
            speaker = "CALLER" if num_segments % 2 == 0 else "OPERATOR"

            # Build TranscriptSegment
            segment = TranscriptSegment(
                time=format_timestamp(elapsed),
                speaker=speaker,
                text=transcript_data["text"],
                words=[WordTimestamp(**w) for w in transcript_data["words"]],
                language=transcript_data["language"],
                prosody=ProsodyFeatures(**prosody) if isinstance(prosody, dict) else prosody,
                ambient=ambient,
                isRisk=False,  # Will be set by analyzer
            )

            # Add to session
            call_sessions[sid].add_segment(segment)

            # Compute baseline prosody from first 60 seconds
            if elapsed < 60 and not call_sessions[sid].baseline_prosody:
                # Use first segment's prosody as baseline
                if segment.prosody.speaking_rate_wpm is not None:
                    call_sessions[sid].baseline_prosody = segment.prosody

            t_build = time.time()

            # Emit to frontend
            logger.info(f"[Chunk {chunk_count}] → Emitting to frontend...")
            await sio.emit("transcript_update", segment.model_dump(), to=sid)

            t_emit = time.time()

            # Log timing breakdown
            logger.info(
                f"[Chunk {chunk_count}] ⏱ Total latency: {t_emit-t_start:.2f}s "
                f"(Sarvam: {t_transcribe-t_start:.2f}s, build: {t_build-t_transcribe:.2f}s, emit: {t_emit-t_build:.2f}s)"
            )

    except Exception as e:
        logger.error(f"Audio pipeline error: {e}", exc_info=True)
        # Emit system error message
        error_segment = TranscriptSegment(
            time=format_timestamp(time.time() - call_start_time),
            speaker="SYSTEM",
            text=f"[System error: {str(e)}]",
            isRisk=False,
        )
        await sio.emit("transcript_update", error_segment.model_dump(), to=sid)


@sio.event
async def connect(sid, environ, auth):
    logger.info(f"Client connected: {sid}")
    call_sessions[sid] = MultimodalTranscript()
    client_tasks[sid] = [
        asyncio.create_task(emit_analysis_loop(sid)),
        asyncio.create_task(emit_transcript_loop(sid)),
    ]


@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")
    call_sessions.pop(sid, None)
    for task in client_tasks.pop(sid, []):
        task.cancel()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
