"""
Append Layer 5 decisions to MongoDB `audit_decisions` (parallel to MCP hash-chain file).
Non-blocking: scheduled as a background task from the analyze pipeline.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


async def insert_audit_decision(
    db: AsyncIOMotorDatabase,
    *,
    session_id: str,
    record_id: Optional[str],
    input_text: str,
    risk: str,
    confidence: float,
    reasoning: dict[str, Any],
    transparency: dict[str, Any],
    operator_action: str = "pending",
    stt_reliable: bool = True,
    privacy_redactions: Optional[list[str]] = None,
) -> None:
    doc = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "record_id": record_id,
        "input_text": input_text,
        "risk": risk,
        "confidence": float(confidence),
        "reasoning": reasoning,
        "transparency": transparency,
        "operator_action": operator_action,
        "stt_reliable": stt_reliable,
        "privacy_redactions": privacy_redactions or [],
    }
    await db.audit_decisions.insert_one(doc)


def schedule_audit_log(
    db: Optional[AsyncIOMotorDatabase],
    *,
    session_id: str,
    record_id: Optional[str],
    input_text: str,
    risk: str,
    confidence: float,
    reasoning: dict[str, Any],
    transparency: dict[str, Any],
    operator_action: str = "pending",
    stt_reliable: bool = True,
    privacy_redactions: Optional[list[str]] = None,
) -> None:
    if db is None:
        return

    async def _run() -> None:
        try:
            await insert_audit_decision(
                db,
                session_id=session_id,
                record_id=record_id,
                input_text=input_text,
                risk=risk,
                confidence=confidence,
                reasoning=reasoning,
                transparency=transparency,
                operator_action=operator_action,
                stt_reliable=stt_reliable,
                privacy_redactions=privacy_redactions,
            )
        except Exception as e:
            logger.warning("audit_decisions insert failed: %s", e)

    asyncio.create_task(_run())
