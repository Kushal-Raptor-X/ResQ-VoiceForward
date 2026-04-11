"""
mcp/server.py — MCP tool exposure for VoiceForward agents.

Exposes:
  analyze_text(text, session_id)
  get_resources(text)
  generate_suggestion(text)
  get_context(session_id)
"""
from fastapi import APIRouter

from agents.analysis_agent import analyze
from agents.context_agent import get_context
from agents.llm_agent import generate_suggestion
from agents.resource_agent import get_resources

router = APIRouter(prefix="/mcp", tags=["MCP Tools"])


@router.post("/analyze_text")
async def mcp_analyze_text(body: dict):
    """
    MCP Tool: analyze_text
    Input:  { "text": "...", "session_id": "..." }
    Output: { "risk", "confidence", "emotion", "signals" }
    """
    text = body.get("text", "")
    result = await analyze(text)
    return {"tool": "analyze_text", "result": result}


@router.post("/get_resources")
async def mcp_get_resources(body: dict):
    """
    MCP Tool: get_resources
    Input:  { "text": "...", "location": "optional" }
    Output: { "type", "resources": [...] }
    """
    text = body.get("text", "")
    location = body.get("location")
    result = await get_resources(text, location)
    return {"tool": "get_resources", "result": result}


@router.post("/generate_suggestion")
async def mcp_generate_suggestion(body: dict):
    """
    MCP Tool: generate_suggestion
    Input:  { "text": "...", "risk": "HIGH" }
    Output: { "empathetic_response", "follow_up_question" }
    """
    text = body.get("text", "")
    risk = body.get("risk", "HIGH")
    result = await generate_suggestion(text, risk=risk)
    return {"tool": "generate_suggestion", "result": result}


@router.post("/get_context")
async def mcp_get_context(body: dict):
    """
    MCP Tool: get_context
    Input:  { "session_id": "..." }
    Output: { "messages", "escalation_trend", "message_count" }
    """
    session_id = body.get("session_id", "")
    result = await get_context(session_id)
    return {"tool": "get_context", "result": result}
