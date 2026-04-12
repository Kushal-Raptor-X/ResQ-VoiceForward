import asyncio
import logging
import os
import time

import numpy as np
import socketio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ambient_classifier import classify_ambient_audio
from analyzer import analyze_transcript
from audio_capture import stream_audio_chunks
from config.db import close_db, connect_db, get_db, is_connected
from logCall import get_memory_store, log_call, update_call_action
from models import MultimodalTranscript, ProsodyFeatures, TranscriptSegment, WordTimestamp
from prosody_analyzer import extract_prosody_features
from transcriber import start_mock_transcription, stream_transcription

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


# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

@fastapi_app.on_event("startup")
async def startup():
    """Connect to MongoDB on startup."""
    await connect_db()


@fastapi_app.on_event("shutdown")
async def shutdown():
    """Close MongoDB connection on shutdown."""
    await close_db()


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@fastapi_app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": int(time.time()),
        "mongodb": "connected" if is_connected() else "offline (in-memory fallback)",
    }


@fastapi_app.get("/db-status")
async def db_status():
    """Check MongoDB connection status and document counts."""
    if not is_connected():
        mem_store = get_memory_store()
        return {
            "connected": False,
            "storage": "in-memory",
            "in_memory_records": len(mem_store),
            "message": "MongoDB offline. Using in-memory fallback.",
        }
    db = get_db()
    try:
        count = await db.calls.count_documents({})
        return {
            "connected": True,
            "storage": "MongoDB Atlas",
            "total_calls_logged": count,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@fastapi_app.get("/calls")
async def get_calls(limit: int = 50, skip: int = 0):
    """Get call logs from MongoDB or in-memory store."""
    db = get_db()
    
    if db is None:
        # In-memory fallback
        mem_store = get_memory_store()
        return {
            "calls": mem_store[skip:skip+limit],
            "total": len(mem_store),
            "storage": "in-memory"
        }
    
    try:
        # Fetch from MongoDB
        cursor = db.calls.find().sort("created_at", -1).skip(skip).limit(limit)
        calls = await cursor.to_list(length=limit)
        total = await db.calls.count_documents({})
        
        # Convert ObjectId to string for JSON serialization
        for call in calls:
            call["_id"] = str(call["_id"])
        
        return {
            "calls": calls,
            "total": total,
            "storage": "MongoDB Atlas"
        }
    except Exception as e:
        logger.error(f"Failed to fetch calls: {e}")
        return {"error": str(e), "calls": [], "total": 0}


@fastapi_app.get("/calls/{call_id}")
async def get_call_details(call_id: str):
    """Get detailed information about a specific call."""
    db = get_db()
    
    if db is None:
        # In-memory fallback
        mem_store = get_memory_store()
        for call in mem_store:
            if call.get("_id") == call_id:
                return {"call": call, "storage": "in-memory"}
        return {"error": "Call not found", "call_id": call_id}
    
    try:
        from bson import ObjectId
        call = await db.calls.find_one({"_id": ObjectId(call_id)})
        
        if call:
            call["_id"] = str(call["_id"])
            return {"call": call, "storage": "MongoDB Atlas"}
        else:
            return {"error": "Call not found", "call_id": call_id}
    except Exception as e:
        logger.error(f"Failed to fetch call {call_id}: {e}")
        return {"error": str(e), "call_id": call_id}


@fastapi_app.delete("/calls/{call_id}")
async def delete_call(call_id: str):
    """Delete a specific call log."""
    db = get_db()
    
    if db is None:
        # In-memory fallback
        mem_store = get_memory_store()
        for i, call in enumerate(mem_store):
            if call.get("_id") == call_id:
                mem_store.pop(i)
                return {"success": True, "message": "Call deleted from in-memory store", "call_id": call_id}
        return {"success": False, "error": "Call not found", "call_id": call_id}
    
    try:
        from bson import ObjectId
        result = await db.calls.delete_one({"_id": ObjectId(call_id)})
        
        if result.deleted_count > 0:
            return {"success": True, "message": "Call deleted from MongoDB", "call_id": call_id}
        else:
            return {"success": False, "error": "Call not found", "call_id": call_id}
    except Exception as e:
        logger.error(f"Failed to delete call {call_id}: {e}")
        return {"success": False, "error": str(e), "call_id": call_id}


@fastapi_app.delete("/calls")
async def delete_all_calls():
    """Delete all call logs (use with caution!)."""
    db = get_db()
    
    if db is None:
        # In-memory fallback
        mem_store = get_memory_store()
        count = len(mem_store)
        mem_store.clear()
        return {"success": True, "message": f"Deleted {count} calls from in-memory store", "deleted_count": count}
    
    try:
        result = await db.calls.delete_many({})
        return {"success": True, "message": f"Deleted {result.deleted_count} calls from MongoDB", "deleted_count": result.deleted_count}
    except Exception as e:
        logger.error(f"Failed to delete all calls: {e}")
        return {"success": False, "error": str(e)}


@fastapi_app.post("/calls/{call_id}/action")
async def update_action(call_id: str, action: str, outcome: str = "unknown"):
    """Update operator action for a call."""
    db = get_db()
    await update_call_action(db, call_id, action, outcome)
    return {"success": True, "call_id": call_id, "action": action, "outcome": outcome}


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
    Logs each analysis to MongoDB for Layer 4 & 5 compliance.
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
            
            # Log to MongoDB (Layer 4 & 5)
            db = get_db()
            transcript_text = "\n".join([f"[{seg.time}] {seg.speaker}: {seg.text}" for seg in session.segments])
            
            try:
                # Convert agent_breakdown to dict if it's a Pydantic model
                agent_verdicts_dict = (
                    analysis.agent_breakdown.model_dump() 
                    if hasattr(analysis.agent_breakdown, 'model_dump') 
                    else analysis.agent_breakdown
                )
                
                record_id = await log_call(
                    db=db,
                    session_id=sid,
                    transcript=transcript_text,
                    phrases=analysis.triggered_signals,
                    risk_level=analysis.risk_level,
                    risk_score=analysis.risk_score,
                    confidence=analysis.confidence,
                    reasoning=[analysis.conflict_resolution or analysis.conflict],
                    agent_verdicts=agent_verdicts_dict,
                    triggered_signals=analysis.triggered_signals,
                    suggested_response=analysis.suggested_response,
                    operator_action="pending",
                    outcome="unknown",
                )
                logger.info(f"✓ Logged to database: {record_id}")
            except Exception as log_error:
                logger.error(f"Failed to log call: {log_error}", exc_info=True)
            
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
    Real-time WebSocket streaming pipeline: capture → stream to Sarvam → emit transcripts.
    Uses Sarvam V3 WebSocket API for true real-time transcription with minimal latency.
    """
    audio_source = os.getenv("AUDIO_SOURCE", "mic")
    call_start_time = time.time()

    logger.info(f"Starting WebSocket streaming pipeline for session {sid} with source: {audio_source}")

    # Initialize session
    call_sessions[sid] = MultimodalTranscript()

    try:
        # Create async generator that converts numpy audio chunks to WAV bytes
        async def audio_byte_stream():
            """Convert numpy audio chunks to WAV bytes for WebSocket streaming."""
            import io
            import scipy.io.wavfile
            
            async for audio_chunk in stream_audio_chunks(source=audio_source):
                # Convert numpy array to WAV bytes
                if audio_chunk.dtype != np.float32:
                    audio_chunk = audio_chunk.astype(np.float32)
                
                # Convert float32 [-1, 1] to int16 [-32768, 32767]
                audio_int16 = (audio_chunk * 32767).astype(np.int16)
                
                # Write to bytes buffer
                buffer = io.BytesIO()
                scipy.io.wavfile.write(buffer, 16000, audio_int16)
                buffer.seek(0)
                wav_bytes = buffer.read()
                
                yield wav_bytes
        
        # Stream transcription results from Sarvam WebSocket
        current_segment_text = ""
        segment_start_time = None
        
        async for event in stream_transcription(
            audio_stream=audio_byte_stream(),
            language_code="en-IN",
            mode="transcribe",
            vad_signals=True,
            high_vad_sensitivity=False,
        ):
            elapsed = time.time() - call_start_time
            
            if event["type"] == "speech_start":
                # Start of new speech segment
                segment_start_time = elapsed
                current_segment_text = ""
                logger.debug(f"🎤 Speech started at {format_timestamp(elapsed)}")
            
            elif event["type"] == "transcript":
                # Received transcript (partial or final)
                text = event.get("text", "").strip()
                is_partial = event.get("partial", False)
                
                if not text:
                    continue
                
                if is_partial:
                    # Update current segment text (don't emit yet)
                    current_segment_text = text
                    logger.debug(f"→ Partial: {text[:50]}...")
                else:
                    # Final transcript - emit to frontend
                    current_segment_text = text
                    
                    # Determine speaker (alternating pattern)
                    num_segments = len(call_sessions[sid].segments)
                    speaker = "CALLER" if num_segments % 2 == 0 else "OPERATOR"
                    
                    # Build TranscriptSegment
                    segment = TranscriptSegment(
                        time=format_timestamp(segment_start_time or elapsed),
                        speaker=speaker,
                        text=current_segment_text,
                        words=[],  # Word timestamps available in event["words"] if needed
                        language=event.get("language", "en-IN"),
                        prosody=ProsodyFeatures(),  # Use defaults for speed
                        ambient={"primary_class": "unknown", "confidence": 0.0, "secondary_classes": [], "risk_relevant": False},
                        isRisk=False,  # Will be set by analyzer
                    )
                    
                    # Add to session
                    call_sessions[sid].add_segment(segment)
                    
                    # Emit to frontend
                    logger.info(f"✓ Transcript: [{speaker}] {text[:80]}...")
                    await sio.emit("transcript_update", segment.model_dump(), to=sid)
                    
                    # Reset for next segment
                    current_segment_text = ""
                    segment_start_time = None
            
            elif event["type"] == "speech_end":
                logger.debug(f"🔇 Speech ended at {format_timestamp(elapsed)}")
            
            elif event["type"] == "error":
                logger.error(f"Transcription error: {event.get('text', 'Unknown error')}")
                # Emit error to frontend
                error_segment = TranscriptSegment(
                    time=format_timestamp(elapsed),
                    speaker="SYSTEM",
                    text=f"[Transcription error: {event.get('text', 'Unknown')}]",
                    isRisk=False,
                )
                await sio.emit("transcript_update", error_segment.model_dump(), to=sid)

    except Exception as e:
        logger.error(f"WebSocket streaming pipeline error: {e}", exc_info=True)
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
