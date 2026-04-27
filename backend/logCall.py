"""
logCall.py — Reusable, non-blocking call logging function.
"""
import asyncio
from typing import Any, Optional

from models.Call import CallDocument, CallModel
from privacy_filter import privacy_filter

# In-memory fallback store (used when MongoDB is offline)
_memory_store: list[dict] = []

# Risk phrases used for phrase extraction (shared with intelligence.py)
_RISK_PHRASES = [
    "giving up", "end it", "decided", "no way forward", "better off without",
    "made my peace", "wrote letters", "final", "can't go on", "hopeless",
    "no point", "tired of living", "want to die", "hurt myself", "not here",
    "disappear", "burden", "worthless", "alone", "nobody cares",
    "i've decided", "no reason", "last time", "goodbye", "farewell",
]


async def log_call(
    db,                          # AsyncIOMotorDatabase or None
    session_id: str,
    transcript: str,
    phrases: list[str],
    risk_level: str,
    risk_score: int,
    confidence: str,
    reasoning: list[str],
    agent_verdicts: dict,
    triggered_signals: list[str],
    suggested_response: str = "",
    operator_action: str = "pending",
    outcome: str = "unknown",
    *,
    risk_timeline: Optional[list[dict[str, Any]]] = None,
    stt_confidence: Optional[float] = None,
    stt_reliable: bool = True,
    transparency: Optional[dict[str, Any]] = None,
    resources_snapshot: Optional[list[dict[str, Any]]] = None,
) -> Optional[str]:
    """
    Persist one call analysis record.
    - Transcript is privacy-filtered before storage (no raw PII in MongoDB).
    - Uses upsert to update existing session records instead of creating duplicates.
    - Falls back to in-memory if MongoDB is offline.
    Returns the record _id (MongoDB ObjectId or UUID string).
    """
    redacted, redactions = privacy_filter(transcript)
    doc = CallDocument(
        session_id=session_id,
        transcript=redacted,
        phrases=phrases,
        risk_level=risk_level,
        risk_score=risk_score,
        confidence=confidence,
        reasoning=reasoning,
        agent_verdicts=agent_verdicts,
        triggered_signals=triggered_signals,
        suggested_response=suggested_response,
        operator_action=operator_action,
        outcome=outcome,
        risk_timeline=risk_timeline or [],
        privacy_redactions=redactions,
        stt_confidence=stt_confidence,
        stt_reliable=stt_reliable,
        transparency=transparency or {},
        resources_snapshot=resources_snapshot or [],
    )

    # Try MongoDB first
    if db is not None:
        try:
            model = CallModel(db)
            record_id = await model.upsert(doc)  # Use upsert to avoid duplicate records
            if record_id:
                print(f"[logCall] ✓ Saved/updated in Atlas (id={record_id}, risk={risk_level}, session={session_id})")
                return record_id
            else:
                print(f"[logCall] ✗ Atlas upsert returned None — falling back to memory")
        except Exception as e:
            print(f"[logCall] ✗ MongoDB write failed: {type(e).__name__}: {e}")

    # In-memory fallback - check if session exists and update, otherwise create new
    fallback = doc.to_mongo()
    fallback.pop("_id", None)
    
    for i, existing_doc in enumerate(_memory_store):
        if existing_doc.get("session_id") == session_id:
            # Update existing in-memory record
            existing_doc["risk_level"] = risk_level
            existing_doc["risk_score"] = risk_score
            existing_doc["confidence"] = confidence
            existing_doc["reasoning"] = reasoning
            existing_doc["agent_verdicts"] = agent_verdicts
            existing_doc["triggered_signals"] = triggered_signals
            existing_doc["suggested_response"] = suggested_response
            existing_doc["operator_action"] = operator_action
            existing_doc["outcome"] = outcome
            existing_doc["transparency"] = transparency or {}
            existing_doc["resources_snapshot"] = resources_snapshot or []
            
            # Append phrases (avoid duplicates)
            for phrase in phrases:
                if phrase not in existing_doc.get("phrases", []):
                    existing_doc["phrases"].append(phrase)
            
            # Append transcript
            if transcript:
                existing_doc["transcript"] = existing_doc.get("transcript", "") + "\n" + transcript
            
            # Append to risk_timeline
            if risk_timeline:
                existing_doc["risk_timeline"] = existing_doc.get("risk_timeline", []) + risk_timeline
            
            # Append privacy_redactions
            if redactions:
                existing_doc["privacy_redactions"] = existing_doc.get("privacy_redactions", []) + redactions
            
            print(f"[logCall] Updated in-memory (session={session_id}, risk={risk_level})")
            return existing_doc.get("_id", session_id)
    
    # No existing session found - create new
    import uuid
    fallback["_id"] = str(uuid.uuid4())
    _memory_store.append(fallback)
    print(f"[logCall] Stored new in-memory (id={fallback['_id']}, risk={risk_level}, session={session_id})")
    return fallback["_id"]


async def update_call_action(
    db,
    record_id: str,
    action: str,
    outcome: str = "unknown",
) -> None:
    """Update operator_action after operator responds. Non-blocking."""
    if db is not None:
        try:
            model = CallModel(db)
            await asyncio.shield(model.update_action(record_id, action, outcome))
            return
        except Exception as e:
            print(f"[logCall] update failed: {e}")

    # In-memory fallback
    for doc in _memory_store:
        if doc.get("_id") == record_id:
            doc["operator_action"] = action
            doc["outcome"] = outcome
            break


def get_memory_store() -> list[dict]:
    """Return in-memory store for analytics fallback."""
    return _memory_store
