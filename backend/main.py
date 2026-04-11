import asyncio
import time

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_transcript
from mock_data import MOCK_ANALYSIS
from transcriber import start_mock_transcription

ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

fastapi_app = FastAPI()
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=ALLOWED_ORIGINS
)
app = socketio.ASGIApp(sio, fastapi_app)
client_tasks: dict[str, list[asyncio.Task]] = {}
call_sessions: dict[str, list[dict[str, str | bool]]] = {}


@fastapi_app.get("/health")
async def health():
    return {"status": "ok", "timestamp": int(time.time())}


def build_transcript_text(lines: list[dict[str, str | bool]]) -> str:
    return "\n".join(
        f"[{line['time']}] {line['speaker']}: {line['text']}" for line in lines
    )


async def emit_analysis_loop(sid: str):
    while True:
        lines = call_sessions.get(sid, [])
        if not lines:
            await sio.emit("analysis_update", MOCK_ANALYSIS, to=sid)
        else:
            analysis = await analyze_transcript(build_transcript_text(lines))
            await sio.emit("analysis_update", analysis.model_dump(), to=sid)
        await asyncio.sleep(4)


async def emit_transcript_loop(sid: str):
    async def emit_line(line):
        call_sessions.setdefault(sid, []).append(line)
        await sio.emit("transcript_update", line, to=sid)

    await start_mock_transcription(emit_line)


@sio.event
async def connect(sid, environ, auth):
    call_sessions[sid] = []
    client_tasks[sid] = [
        asyncio.create_task(emit_analysis_loop(sid)),
        asyncio.create_task(emit_transcript_loop(sid)),
    ]


@sio.event
async def disconnect(sid):
    call_sessions.pop(sid, None)
    for task in client_tasks.pop(sid, []):
        task.cancel()
