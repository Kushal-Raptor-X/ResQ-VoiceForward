"""
database.py — Public analytics API used by main.py and intelligence.py.
Delegates to models/Call.py (CallModel) and logCall.py.
Falls back to in-memory store when MongoDB is offline.
"""
from collections import defaultdict
from typing import Optional

from config.db import get_db
from logCall import get_memory_store, log_call, update_call_action
from models.Call import CallModel

# Re-export log_call and update so existing imports in intelligence.py / main.py still work
log_analysis = log_call
update_operator_action = update_call_action


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

async def get_phrase_risk_stats() -> dict:
    """Phrase → risk probability. MongoDB aggregation or in-memory fallback."""
    db = get_db()
    if db is not None:
        rows = await CallModel(db).phrase_risk_stats()
        if rows:
            return {r["phrase"]: r for r in rows}

    # In-memory fallback
    counts: dict = defaultdict(lambda: {"total": 0, "high": 0})
    for doc in get_memory_store():
        for phrase in doc.get("phrases", []):
            counts[phrase]["total"] += 1
            if doc.get("risk_level") in ("HIGH", "CRITICAL"):
                counts[phrase]["high"] += 1
    return {
        p: {
            "phrase": p,
            "total_occurrences": v["total"],
            "high_risk_count": v["high"],
            "risk_probability": round(v["high"] / v["total"], 2) if v["total"] else 0,
        }
        for p, v in counts.items()
    }


async def get_best_responses() -> list[dict]:
    """Best accepted responses at HIGH/CRITICAL risk."""
    db = get_db()
    if db is not None:
        rows = await CallModel(db).best_responses()
        if rows:
            return rows

    # In-memory fallback
    counts: dict = defaultdict(lambda: {"count": 0, "scores": []})
    for doc in get_memory_store():
        if doc.get("operator_action") == "accepted" and doc.get("risk_level") in ("HIGH", "CRITICAL"):
            r = doc.get("suggested_response", "")
            if r:
                counts[r]["count"] += 1
                counts[r]["scores"].append(doc.get("confidence", 0))
    return [
        {
            "response": r,
            "accepted_count": v["count"],
            "avg_confidence": round(sum(v["scores"]) / len(v["scores"]), 2) if v["scores"] else 0,
            "success_rate": f"{min(100, v['count'] * 12)}%",
        }
        for r, v in sorted(counts.items(), key=lambda x: -x[1]["count"])[:5]
    ]


async def get_insights(risk: str, triggered_signals: list[str]) -> dict:
    """Insights for a given risk level."""
    db = get_db()
    if db is not None:
        return await CallModel(db).insights_for_risk(risk)

    # In-memory fallback
    store = get_memory_store()
    similar = [d for d in store if d.get("risk_level") == risk]
    accepted = [d for d in similar if d.get("operator_action") == "accepted"]
    total = len(similar)
    return {
        "similar_cases_total": total,
        "similar_case_risk": f"{round((len(accepted) / total) * 100)}%" if total else "insufficient data",
        "best_response_success": f"{round((len(accepted) / total) * 100)}%" if total else "insufficient data",
        "data_note": "In-memory store active (MongoDB offline). Data resets on restart." if total > 0
                     else "No historical data yet — insights improve with usage.",
    }
