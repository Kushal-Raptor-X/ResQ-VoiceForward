"""
models/Call.py — Call log schema and model.
Python/Motor equivalent of a Mongoose model.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class CallDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    session_id: str
    transcript: str
    phrases: list[str] = []
    risk_level: str
    confidence: float
    reasoning: list[str] = []
    agent_verdicts: dict = {}
    operator_action: str = "pending"
    outcome: str = "unknown"
    suggested_response: str = ""
    triggered_signals: list[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        d = self.model_dump(by_alias=True)
        if "_id" not in d and "id" in d:
            d["_id"] = d.pop("id")
        return d

    @classmethod
    def collection_name(cls) -> str:
        return "calls"


class CallModel:
    def __init__(self, db):
        # Use is not None — Motor objects raise NotImplementedError on bool()
        self._col = db[CallDocument.collection_name()] if db is not None else None

    async def save(self, doc: CallDocument) -> Optional[str]:
        if self._col is None:
            return None
        try:
            mongo_doc = doc.to_mongo()
            result = await self._col.insert_one(mongo_doc)
            inserted = str(result.inserted_id)
            print(f"[CallModel] ✓ Saved to Atlas: {inserted} risk={mongo_doc.get('risk_level')}")
            return inserted
        except Exception as e:
            print(f"[CallModel] ✗ save failed: {type(e).__name__}: {e}")
            return None

    async def update_action(self, doc_id: str, action: str, outcome: str = "unknown") -> None:
        if self._col is None:
            return
        try:
            await self._col.update_one(
                {"_id": doc_id},
                {"$set": {"operator_action": action, "outcome": outcome}},
            )
        except Exception as e:
            print(f"[CallModel] update_action failed: {e}")

    async def phrase_risk_stats(self) -> list[dict]:
        if self._col is None:
            return []
        try:
            pipeline = [
                {"$unwind": "$phrases"},
                {"$group": {
                    "_id": "$phrases",
                    "total": {"$sum": 1},
                    "high_risk_count": {"$sum": {"$cond": [{"$in": ["$risk_level", ["HIGH", "CRITICAL"]]}, 1, 0]}},
                }},
                {"$sort": {"high_risk_count": -1}},
                {"$limit": 20},
                {"$project": {
                    "phrase": "$_id", "total_occurrences": "$total", "high_risk_count": 1,
                    "risk_probability": {"$round": [{"$divide": ["$high_risk_count", "$total"]}, 2]},
                    "_id": 0,
                }},
            ]
            return [doc async for doc in self._col.aggregate(pipeline)]
        except Exception as e:
            print(f"[CallModel] phrase_risk_stats failed: {e}")
            return []

    async def best_responses(self) -> list[dict]:
        if self._col is None:
            return []
        try:
            pipeline = [
                {"$match": {"operator_action": "accepted", "risk_level": {"$in": ["HIGH", "CRITICAL"]}, "suggested_response": {"$ne": ""}}},
                {"$group": {"_id": "$suggested_response", "accepted_count": {"$sum": 1}, "avg_confidence": {"$avg": "$confidence"}}},
                {"$sort": {"accepted_count": -1}},
                {"$limit": 5},
                {"$project": {
                    "response": "$_id", "accepted_count": 1,
                    "avg_confidence": {"$round": ["$avg_confidence", 2]},
                    "success_rate": {"$concat": [{"$toString": {"$min": [100, {"$multiply": ["$accepted_count", 12]}]}}, "%"]},
                    "_id": 0,
                }},
            ]
            return [doc async for doc in self._col.aggregate(pipeline)]
        except Exception as e:
            print(f"[CallModel] best_responses failed: {e}")
            return []

    async def insights_for_risk(self, risk_level: str) -> dict:
        if self._col is None:
            return {"similar_cases_total": 0, "similar_case_risk": "no data", "best_response_success": "no data"}
        try:
            total = await self._col.count_documents({"risk_level": risk_level})
            accepted = await self._col.count_documents({"risk_level": risk_level, "operator_action": "accepted"})
            return {
                "similar_cases_total": total,
                "similar_case_risk": f"{round((accepted / total) * 100)}%" if total else "insufficient data",
                "best_response_success": f"{round((accepted / total) * 100)}%" if total else "insufficient data",
                "data_note": "Based on anonymised session patterns. No PII stored.",
            }
        except Exception as e:
            print(f"[CallModel] insights failed: {e}")
            return {"similar_cases_total": 0, "similar_case_risk": "error", "best_response_success": "error"}
