"""
main.py — VoiceForward Real-Time Backend

Architecture:
  WebSocket /ws/stream  → parallel multi-agent pipeline
  REST /mcp/*           → MCP tool endpoints
  REST /health          → status + model info

Models loaded ONCE at startup (DistilBERT).
Sarvam AI used for STT + LLM suggestion (async only).
"""
import asyncio
import time

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from mcp.server import router as mcp_router
from websocket import handle_websocket

app = FastAPI(
    title="VoiceForward Real-Time Backend",
    description="Parallel multi-agent crisis helpline assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mcp_router)


# ---------------------------------------------------------------------------
# Startup — pre-warm models
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    print("[main] Starting VoiceForward Real-Time Backend...")
    # DistilBERT is loaded at import time in analysis_agent.py
    # Just verify it's ready
    from agents.analysis_agent import _pipeline, _model_load_error
    if _pipeline:
        print("[main] ✓ DistilBERT ready")
    else:
        print(f"[main] ⚠ DistilBERT not loaded: {_model_load_error}")
    print("[main] ✓ All agents ready. WebSocket at ws://localhost:8001/ws/stream")


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    """
    Main real-time stream endpoint.

    Send JSON:
      { "type": "text", "text": "I feel chest pain", "session_id": "abc" }
      { "type": "audio", "data": "<base64_wav>", "session_id": "abc" }

    Receive JSON stream:
      { "type": "partial", "text": "...", "latency_ms": N }
      { "type": "analysis", "analysis": {...}, "resources": {...}, "report": {...} }
      { "type": "suggestion", "suggestion": {...} }   ← async, arrives later
      { "type": "warning", "message": "..." }
    """
    await handle_websocket(websocket)


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    from agents.analysis_agent import _pipeline, _model_load_error
    from agents.context_agent import get_all_sessions
    return {
        "status": "ok",
        "timestamp": int(time.time()),
        "distilbert": "loaded" if _pipeline else f"failed: {_model_load_error}",
        "active_sessions": len(get_all_sessions()),
    }


@app.post("/analyze")
async def analyze_rest(body: dict):
    """REST fallback for /analyze — same as MCP analyze_text."""
    from agents.analysis_agent import analyze
    text = body.get("text", "")
    return await analyze(text)


@app.get("/demo", response_class=HTMLResponse)
async def demo_ui():
    """Serve the built-in WebSocket test UI."""
    with open("demo.html", "r") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
