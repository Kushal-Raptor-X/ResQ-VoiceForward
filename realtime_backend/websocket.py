"""
websocket.py — Real-time WebSocket endpoint.

Architecture:
  Incoming chunk → STT → EVENT BUS → parallel agents → partial results → frontend
  If risk >= HIGH → background LLM task → send suggestion when ready

Concurrency model:
  - asyncio.create_task for non-blocking dispatch
  - asyncio.gather for parallel agent execution
  - Partial results sent immediately (don't wait for all agents)
"""
import asyncio
import json
import time
import uuid
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from agents.analysis_agent import analyze
from agents.context_agent import add_message, clear_session, get_context, get_context_text
from agents.llm_agent import generate_suggestion
from agents.report_agent import clear_report, update_report
from agents.resource_agent import get_resources
from agents.stt_agent import transcribe_chunk, transcribe_text_mock

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


async def _send(ws: WebSocket, payload: dict) -> None:
    """Safe send — swallows errors if client disconnected."""
    try:
        await ws.send_text(json.dumps(payload))
    except Exception:
        pass


async def _run_parallel_agents(
    text: str,
    session_id: str,
    ws: WebSocket,
    stt_reliable: bool,
) -> dict:
    """
    Run analysis, resource, and report agents in parallel.
    Sends partial results to frontend as each completes.
    Returns aggregated result.
    """
    t0 = time.monotonic()

    # ── Create all tasks simultaneously ──────────────────────────────────
    analysis_task = asyncio.create_task(analyze(text))
    resource_task = asyncio.create_task(get_resources(text))
    context_task  = asyncio.create_task(get_context(session_id))

    # ── Send partial: text received immediately ───────────────────────────
    await _send(ws, {
        "type": "partial",
        "text": text,
        "reliable": stt_reliable,
        "latency_ms": round((time.monotonic() - t0) * 1000),
    })

    # ── Gather all agents (parallel, not sequential) ──────────────────────
    analysis_result, resource_result, context_result = await asyncio.gather(
        analysis_task, resource_task, context_task,
        return_exceptions=True,
    )

    # Handle any agent exceptions gracefully
    if isinstance(analysis_result, Exception):
        analysis_result = {"risk": "HIGH", "confidence": 0.25, "emotion": "unknown", "signals": [], "bert_label": "UNKNOWN"}
    if isinstance(resource_result, Exception):
        resource_result = {"type": "mental_health", "resources": []}
    if isinstance(context_result, Exception):
        context_result = {"session_id": session_id, "messages": [], "escalation_trend": "stable", "message_count": 0}

    # ── Update context memory ─────────────────────────────────────────────
    await add_message(session_id, text, role="caller", risk=analysis_result["risk"])

    # ── Update live report ────────────────────────────────────────────────
    report = await update_report(
        session_id=session_id,
        text=text,
        risk=analysis_result["risk"],
        emotion=analysis_result.get("emotion", "neutral"),
        signals=analysis_result.get("signals", []),
        resources=resource_result,
    )

    latency_ms = round((time.monotonic() - t0) * 1000)

    return {
        "analysis": analysis_result,
        "resources": resource_result,
        "context": context_result,
        "report": report,
        "latency_ms": latency_ms,
    }


async def _background_suggestion(
    text: str,
    session_id: str,
    risk: str,
    ws: WebSocket,
) -> None:
    """
    Background task: generate LLM suggestion and push to frontend.
    Only triggered when risk >= HIGH. Never blocks main pipeline.
    """
    context_text = await get_context_text(session_id)
    suggestion = await generate_suggestion(text, context=context_text, risk=risk)
    await _send(ws, {
        "type": "suggestion",
        "session_id": session_id,
        "risk": risk,
        "suggestion": suggestion,
    })


async def handle_websocket(ws: WebSocket) -> None:
    """
    Main WebSocket handler.

    Message formats accepted:
      Text:  { "type": "text", "text": "...", "session_id": "..." }
      Audio: { "type": "audio", "data": "<base64>", "session_id": "..." }
      Ping:  { "type": "ping" }
    """
    await ws.accept()
    session_id = str(uuid.uuid4())
    await _send(ws, {"type": "connected", "session_id": session_id})

    try:
        while True:
            raw = await ws.receive_text()
            t_recv = time.monotonic()

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                # Treat raw string as plain text input
                msg = {"type": "text", "text": raw}

            msg_type = msg.get("type", "text")
            # Allow client to specify their own session_id
            session_id = msg.get("session_id", session_id)

            if msg_type == "ping":
                await _send(ws, {"type": "pong"})
                continue

            # ── STT: get text from audio or pass-through ──────────────────
            if msg_type == "audio":
                import base64
                audio_bytes = base64.b64decode(msg.get("data", ""))
                stt_result = await transcribe_chunk(audio_bytes)
                text = stt_result["text"]
                stt_reliable = stt_result["reliable"]
                if not stt_reliable:
                    await _send(ws, {
                        "type": "warning",
                        "message": "STT confidence low — transcript may be unreliable",
                        "confidence": stt_result["confidence"],
                    })
            else:
                text = msg.get("text", "").strip()
                stt_result = await transcribe_text_mock(text)
                stt_reliable = True

            if not text:
                continue

            # ── Run parallel agents ───────────────────────────────────────
            result = await _run_parallel_agents(text, session_id, ws, stt_reliable)

            # ── Send full result ──────────────────────────────────────────
            await _send(ws, {
                "type": "analysis",
                "session_id": session_id,
                "text": text,
                "analysis": result["analysis"],
                "resources": result["resources"],
                "report": result["report"],
                "context": {
                    "escalation_trend": result["context"].get("escalation_trend"),
                    "message_count": result["context"].get("message_count"),
                },
                "latency_ms": result["latency_ms"],
                "pipeline_ms": round((time.monotonic() - t_recv) * 1000),
            })

            # ── Trigger async LLM suggestion if risk >= HIGH ──────────────
            risk = result["analysis"]["risk"]
            if RISK_ORDER.get(risk, 0) >= RISK_ORDER["HIGH"]:
                asyncio.create_task(
                    _background_suggestion(text, session_id, risk, ws)
                )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[websocket] Session {session_id} error: {e}")
    finally:
        clear_session(session_id)
        clear_report(session_id)
