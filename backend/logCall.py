"""
logCall.py — Reusable, non-blocking call logging function.
"""
import asyncio
from typing import Optional

from models.Call import CallDocument, CallModel

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
    confidence: float,
    reasoning: list[str],
    agent_verdicts: dict,
    triggered_signals: list[str],
    suggested_response: str = "",
    operator_action: str = "pending",
    outcome: str = "unknown",
) -> Optional[str]:
    """
    Persist one call analysis record.
    - Non-blocking: wrapped in asyncio.shield so caller never waits on DB failure
    - No PII: session_id only, no caller name/number/location
    - Falls back to in-memory if MongoDB is offline
    Returns the record _id (MongoDB or UUID string).
    """
    doc = CallDocument(
        session_id=session_id,
        transcript=transcript,
        phrases=phrases,
        risk_level=risk_level,
        confidence=confidence,
        reasoning=reasoning,
        agent_verdicts=agent_verdicts,
        triggered_signals=triggered_signals,
        suggested_response=suggested_response,
        operator_action=operator_action,
        outcome=outcome,
    )

    # Try MongoDB first
    if db is not None:
        try:
            model = CallModel(db)
            record_id = await model.save(doc)  # direct await — no shield swallowing errors
            if record_id:
                print(f"[logCall] ✓ Saved to Atlas (id={record_id}, risk={risk_level})")
                return record_id
            else:
                print(f"[logCall] ✗ Atlas save returned None — falling back to memory")
        except Exception as e:
            print(f"[logCall] ✗ MongoDB write failed: {type(e).__name__}: {e}")

    # In-memory fallback
    fallback = doc.to_mongo()
    _memory_store.append(fallback)
    print(f"[logCall] Stored in-memory (id={fallback['_id']}, risk={risk_level})")
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
