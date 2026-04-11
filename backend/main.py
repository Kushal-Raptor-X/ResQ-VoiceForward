import asyncio
import time
from datetime import datetime, timezone

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_transcript
from config.db import DB_NAME, close_db, connect_db, get_db, is_connected
from database import get_best_responses, get_insights, get_phrase_risk_stats
from intelligence import run_analyze_pipeline
from learning import generate_learning_insights
from logCall import update_call_action
from mock_data import MOCK_ANALYSIS
from schemas import AnalyzeRequest, OperatorActionLog
from transcriber import start_mock_transcription

ALLOWED_ORIGINS = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:5174", "http://127.0.0.1:5174",
]

fastapi_app = FastAPI(title="VoiceForward API", version="1.0.0")
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=ALLOWED_ORIGINS)
app = socketio.ASGIApp(sio, fastapi_app)

client_tasks: dict[str, list[asyncio.Task]] = {}
call_sessions: dict[str, list[dict]] = {}
action_log: list[dict] = []


# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

@fastapi_app.on_event("startup")
async def startup():
    await connect_db()


@fastapi_app.on_event("shutdown")
async def shutdown():
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
        from logCall import get_memory_store
        mem = get_memory_store()
        return {
            "connected": False,
            "storage": "in-memory",
            "in_memory_records": len(mem),
            "message": "MongoDB offline. Call POST /db-reconnect to retry.",
        }
    db = get_db()
    try:
        count = await db.calls.count_documents({})
        return {
            "connected": True,
            "storage": "MongoDB Atlas",
            "database": DB_NAME,
            "total_calls_logged": count,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@fastapi_app.post("/db-reconnect")
async def db_reconnect():
    """Reconnect to MongoDB without restarting the server."""
    success = await connect_db()
    return {
        "connected": success,
        "message": "Connected to MongoDB Atlas" if success else "Connection failed — check MONGO_URI in backend/.env",
    }


@fastapi_app.get("/insights/learning")
async def learning_insights():
    """
    GET /insights/learning — Featherless AI-powered learning insights.
    Analyses stored call patterns and generates natural language insights.
    """
    return await generate_learning_insights()


@fastapi_app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """POST /analyze — full multi-agent pipeline."""
    try:
        return await run_analyze_pipeline(
            transcript=request.transcript,
            session_id=request.session_id,
        )
    except Exception as e:
        print(f"[analyze] Pipeline exception: {type(e).__name__}: {e}")
        # Return graceful degraded response instead of 500
        import uuid
        from schemas import AnalyzeInsights, AnalyzeResponse
        return AnalyzeResponse(
            session_id=request.session_id or str(uuid.uuid4()),
            risk="HIGH",
            risk_score=75,
            confidence=0.25,
            confidence_label="UNCERTAIN",
            reasoning=[f"Pipeline error — using conservative fallback: {str(e)[:100]}"],
            triggered_signals=[],
            agent_breakdown={},
            conflict="",
            conflict_resolution="",
            suggested_response="",
            operator_note="AI pipeline temporarily unavailable. Use your training.",
            resources=[],
            insights=AnalyzeInsights(
                similar_case_risk="unavailable",
                best_response_success="unavailable",
                data_note="Pipeline error — defaulting to HIGH risk conservatively.",
            ),
            warnings=["PIPELINE ERROR — AI analysis unavailable. Defaulting to HIGH risk.", str(e)[:200]],
            record_id=None,
        )


@fastapi_app.post("/analyze/{record_id}/action")
async def record_action(record_id: str, body: dict):
    """POST /analyze/{record_id}/action — log operator response."""
    action = body.get("action", "accepted")
    outcome = body.get("outcome", "unknown")
    await update_call_action(get_db(), record_id, action, outcome)
    return {"status": "logged", "record_id": record_id, "action": action, "outcome": outcome}


@fastapi_app.get("/insights/phrases")
async def phrase_stats():
    stats = await get_phrase_risk_stats()
    return {"phrase_risk_stats": stats, "count": len(stats)}


@fastapi_app.get("/insights/responses")
async def best_responses_endpoint():
    responses = await get_best_responses()
    return {"best_responses": responses, "count": len(responses)}


@fastapi_app.get("/insights/{risk_level}")
async def insights_for_risk(risk_level: str):
    return await get_insights(risk_level.upper(), [])


@fastapi_app.get("/audit-log")
async def get_audit_log():
    return {"entries": action_log, "count": len(action_log)}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_transcript_text(lines: list[dict]) -> str:
    return "\n".join(
        f"[{line['time']}] {line['speaker']}: {line['text']}" for line in lines
    )


# ---------------------------------------------------------------------------
# Per-client socket loops
# ---------------------------------------------------------------------------

async def emit_analysis_loop(sid: str):
    """LLM analysis every 15s — respects Featherless rate limits."""
    await asyncio.sleep(8)
    while True:
        lines = call_sessions.get(sid, [])
        if lines:
            try:
                analysis = await analyze_transcript(build_transcript_text(lines))
                await sio.emit("analysis_update", analysis.model_dump(), to=sid)
            except Exception as e:
                print(f"[analysis_loop] Error for {sid}: {e}")
                await sio.emit("analysis_update", MOCK_ANALYSIS, to=sid)
        await asyncio.sleep(15)


async def emit_transcript_loop(sid: str):
    async def on_line(line):
        call_sessions.setdefault(sid, []).append(line)
        await sio.emit("transcript_update", line, to=sid)

    async def on_segment_analysis(analysis_dict):
        await sio.emit("analysis_update", analysis_dict, to=sid)

    await start_mock_transcription(on_line, on_segment_analysis)


# ---------------------------------------------------------------------------
# Socket.io events
# ---------------------------------------------------------------------------

@sio.event
async def connect(sid, environ, auth):
    call_sessions[sid] = []
    client_tasks[sid] = [
        asyncio.create_task(emit_analysis_loop(sid)),
        asyncio.create_task(emit_transcript_loop(sid)),
    ]
    await sio.emit("analysis_update", MOCK_ANALYSIS, to=sid)


@sio.event
async def disconnect(sid):
    call_sessions.pop(sid, None)
    for task in client_tasks.pop(sid, []):
        task.cancel()


@sio.event
async def operator_action(sid, data):
    entry = OperatorActionLog(
        sid=sid,
        action=data.get("action", "ACCEPT"),
        suggestion=data.get("suggestion", ""),
        risk_level=data.get("risk_level", "UNKNOWN"),
        risk_score=data.get("risk_score", 0),
        confidence=data.get("confidence", "UNKNOWN"),
        reasoning=data.get("reasoning", ""),
        timestamp=datetime.now(timezone.utc).isoformat(),
        resource_used=data.get("resource_used"),
    )
    action_log.append(entry.model_dump())
    if data.get("record_id"):
        await update_call_action(
            get_db(), data["record_id"],
            entry.action.lower(),
            data.get("outcome", "unknown"),
        )
    print(f"[audit] {entry.action} by {sid} — risk={entry.risk_level}")
