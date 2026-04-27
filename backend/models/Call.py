"""
models/Call.py — MongoDB document model for call logs (Layer 4 & 5).
"""
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from bson import ObjectId


class CallDocument:
    """
    Call log document structure for MongoDB.
    Includes Layer 4 (longitudinal learning) and Layer 5 (audit, transparency) data.
    """

    def __init__(
        self,
        session_id: str,
        transcript: str,
        phrases: list[str],
        risk_level: str,
        confidence: str,  # Changed from float to str (HIGH/MEDIUM/LOW/UNCERTAIN)
        reasoning: list[str],
        agent_verdicts: dict,
        triggered_signals: list[str],
        suggested_response: str = "",
        operator_action: str = "pending",
        outcome: str = "unknown",
        risk_timeline: Optional[list[dict[str, Any]]] = None,
        privacy_redactions: Optional[list[dict[str, Any]]] = None,
        stt_confidence: Optional[float] = None,
        stt_reliable: bool = True,
        transparency: Optional[dict[str, Any]] = None,
        resources_snapshot: Optional[list[dict[str, Any]]] = None,
        risk_score: int = 0,
    ):
        self.session_id = session_id
        self.transcript = transcript
        self.phrases = phrases
        self.risk_level = risk_level
        self.confidence = confidence
        self.reasoning = reasoning
        self.agent_verdicts = agent_verdicts
        self.triggered_signals = triggered_signals
        self.suggested_response = suggested_response
        self.operator_action = operator_action
        self.outcome = outcome
        self.risk_timeline = risk_timeline or []
        self.privacy_redactions = privacy_redactions or []
        self.stt_confidence = stt_confidence
        self.stt_reliable = stt_reliable
        self.transparency = transparency or {}
        self.resources_snapshot = resources_snapshot or []
        self.risk_score = risk_score
        self.created_at = datetime.utcnow()

    def to_mongo(self) -> dict:
        """Convert to MongoDB document format."""
        return {
            "_id": str(uuid4()),  # Use UUID for in-memory compatibility
            "session_id": self.session_id,
            "transcript": self.transcript,
            "phrases": self.phrases,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "agent_verdicts": self.agent_verdicts,
            "triggered_signals": self.triggered_signals,
            "suggested_response": self.suggested_response,
            "operator_action": self.operator_action,
            "outcome": self.outcome,
            "risk_timeline": self.risk_timeline,
            "privacy_redactions": self.privacy_redactions,
            "stt_confidence": self.stt_confidence,
            "stt_reliable": self.stt_reliable,
            "transparency": self.transparency,
            "resources_snapshot": self.resources_snapshot,
            "created_at": self.created_at,
        }


class CallModel:
    """MongoDB operations for call logs."""

    def __init__(self, db):
        self.db = db
        self.collection = db.calls

    async def save(self, doc: CallDocument) -> Optional[str]:
        """Save a call document to MongoDB."""
        try:
            mongo_doc = doc.to_mongo()
            # Remove _id for MongoDB to generate its own ObjectId
            mongo_doc.pop("_id", None)
            result = await self.collection.insert_one(mongo_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"[CallModel] Failed to save: {e}")
            return None

    async def get_by_session_id(self, session_id: str) -> Optional[dict]:
        """Get a call document by session_id."""
        try:
            return await self.collection.find_one({"session_id": session_id})
        except Exception as e:
            print(f"[CallModel] Failed to get by session_id: {e}")
            return None

    async def upsert(self, doc: CallDocument) -> Optional[str]:
        """
        Upsert a call document based on session_id.
        If a record with the same session_id exists, update it (append transcript, timeline, etc.).
        If not, create a new record.
        Returns the record _id.
        """
        try:
            existing = await self.get_by_session_id(doc.session_id)
            
            if existing:
                # Update existing record - append new data
                update_ops = {
                    "$set": {
                        "risk_level": doc.risk_level,
                        "risk_score": doc.risk_score,
                        "confidence": doc.confidence,
                        "reasoning": doc.reasoning,
                        "agent_verdicts": doc.agent_verdicts,
                        "triggered_signals": doc.triggered_signals,
                        "suggested_response": doc.suggested_response,
                        "operator_action": doc.operator_action,
                        "outcome": doc.outcome,
                        "transparency": doc.transparency,
                        "resources_snapshot": doc.resources_snapshot,
                    },
                    "$push": {
                        "phrases": {"$each": doc.phrases},
                    },
                }
                
                # Append to transcript (keep most recent at the end)
                if doc.transcript:
                    update_ops["$push"]["transcript"] = doc.transcript
                
                # Append to risk_timeline
                if doc.risk_timeline:
                    update_ops["$push"]["risk_timeline"] = {"$each": doc.risk_timeline}
                
                # Append to privacy_redactions
                if doc.privacy_redactions:
                    update_ops["$push"]["privacy_redactions"] = {"$each": doc.privacy_redactions}
                
                await self.collection.update_one(
                    {"session_id": doc.session_id},
                    update_ops
                )
                return str(existing["_id"])
            else:
                # Create new record
                mongo_doc = doc.to_mongo()
                mongo_doc.pop("_id", None)
                result = await self.collection.insert_one(mongo_doc)
                return str(result.inserted_id)
        except Exception as e:
            print(f"[CallModel] Failed to upsert: {e}")
            return None

    async def update_action(self, record_id: str, action: str, outcome: str) -> bool:
        """Update operator action for a call."""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(record_id)},
                {"$set": {"operator_action": action, "outcome": outcome}},
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"[CallModel] Failed to update action: {e}")
            return False

    async def phrase_risk_stats(self) -> list[dict]:
        """Aggregate phrase risk statistics."""
        try:
            pipeline = [
                {"$unwind": "$phrases"},
                {
                    "$group": {
                        "_id": "$phrases",
                        "total_occurrences": {"$sum": 1},
                        "high_risk_count": {
                            "$sum": {
                                "$cond": [
                                    {"$in": ["$risk_level", ["HIGH", "CRITICAL"]]},
                                    1,
                                    0,
                                ]
                            }
                        },
                    }
                },
                {
                    "$project": {
                        "phrase": "$_id",
                        "total_occurrences": 1,
                        "high_risk_count": 1,
                        "risk_probability": {
                            "$cond": [
                                {"$eq": ["$total_occurrences", 0]},
                                0,
                                {"$divide": ["$high_risk_count", "$total_occurrences"]},
                            ]
                        },
                    }
                },
                {"$sort": {"risk_probability": -1}},
            ]
            cursor = self.collection.aggregate(pipeline)
            return await cursor.to_list(length=100)
        except Exception as e:
            print(f"[CallModel] phrase_risk_stats failed: {e}")
            return []

    async def best_responses(self) -> list[dict]:
        """Get best accepted responses at HIGH/CRITICAL risk."""
        try:
            pipeline = [
                {
                    "$match": {
                        "operator_action": "accepted",
                        "risk_level": {"$in": ["HIGH", "CRITICAL"]},
                    }
                },
                {
                    "$group": {
                        "_id": "$suggested_response",
                        "accepted_count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence"},
                    }
                },
                {
                    "$project": {
                        "response": "$_id",
                        "accepted_count": 1,
                        "avg_confidence": {"$round": ["$avg_confidence", 2]},
                        "success_rate": {
                            "$concat": [
                                {"$toString": {"$multiply": ["$accepted_count", 12]}},
                                "%",
                            ]
                        },
                    }
                },
                {"$sort": {"accepted_count": -1}},
                {"$limit": 5},
            ]
            cursor = self.collection.aggregate(pipeline)
            return await cursor.to_list(length=5)
        except Exception as e:
            print(f"[CallModel] best_responses failed: {e}")
            return []

    async def supervisor_insights(self) -> dict:
        """Supervisor dashboard insights."""
        try:
            # Top effective phrases
            phrase_pipeline = [
                {"$match": {"outcome": "resolved", "operator_action": "accepted"}},
                {"$unwind": "$phrases"},
                {
                    "$group": {
                        "_id": "$phrases",
                        "hits": {"$sum": 1},
                    }
                },
                {
                    "$lookup": {
                        "from": "calls",
                        "let": {"phrase": "$_id"},
                        "pipeline": [
                            {"$unwind": "$phrases"},
                            {"$match": {"$expr": {"$eq": ["$phrases", "$$phrase"]}}},
                            {"$count": "total"},
                        ],
                        "as": "total_count",
                    }
                },
                {
                    "$project": {
                        "phrase": "$_id",
                        "hits": 1,
                        "samples": {"$arrayElemAt": ["$total_count.total", 0]},
                        "success_rate": {
                            "$divide": ["$hits", {"$arrayElemAt": ["$total_count.total", 0]}]
                        },
                    }
                },
                {"$match": {"samples": {"$gte": 1}}},
                {"$sort": {"success_rate": -1}},
                {"$limit": 8},
            ]
            cursor = self.collection.aggregate(phrase_pipeline)
            top_phrases = await cursor.to_list(length=8)

            return {
                "top_effective_phrases": top_phrases,
                "high_risk_patterns": [],
                "resource_gaps": [],
                "source": "MongoDB",
            }
        except Exception as e:
            print(f"[CallModel] supervisor_insights failed: {e}")
            return {"source": "error", "error": str(e)}

    async def insights_for_risk(self, risk: str) -> dict:
        """Get insights for a specific risk level."""
        try:
            total = await self.collection.count_documents({"risk_level": risk})
            accepted = await self.collection.count_documents(
                {"risk_level": risk, "operator_action": "accepted"}
            )

            success_rate = round((accepted / total) * 100) if total > 0 else 0

            return {
                "similar_cases_total": total,
                "similar_case_risk": f"{success_rate}%",
                "best_response_success": f"{success_rate}%",
                "data_note": f"Based on {total} historical cases at {risk} risk level.",
            }
        except Exception as e:
            print(f"[CallModel] insights_for_risk failed: {e}")
            return {
                "similar_cases_total": 0,
                "similar_case_risk": "insufficient data",
                "best_response_success": "insufficient data",
                "data_note": f"Error: {e}",
            }
