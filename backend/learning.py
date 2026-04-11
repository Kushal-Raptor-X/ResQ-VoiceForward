"""
learning.py — Featherless AI-powered learning system (Layer 4).

Uses stored call data from MongoDB to generate:
- Natural language insights about risk patterns
- Operator response effectiveness analysis
- Escalation prediction from early call signals

All inference done via Featherless AI (deepseek-ai/DeepSeek-V3-0324).
No external ML libraries — the LLM IS the learning engine.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from config.db import get_db
from logCall import get_memory_store

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

_client = AsyncOpenAI(
    api_key=os.getenv("FEATHERLESS_API_KEY"),
    base_url="https://api.featherless.ai/v1",
)
MODEL = "deepseek-ai/DeepSeek-V3-0324"

LEARNING_SYSTEM_PROMPT = """You are the Learning Engine for VoiceForward, a crisis helpline AI system.
You analyse anonymised call data patterns and generate actionable insights for supervisors.
Be concise, clinical, and specific. Always cite numbers from the data provided.
Return ONLY valid JSON, no markdown, no preamble."""


async def _fetch_call_stats() -> dict:
    """Pull aggregated stats from MongoDB or in-memory store."""
    db = get_db()
    stats = {
        "total_calls": 0,
        "by_risk": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
        "by_action": {"pending": 0, "accepted": 0, "rejected": 0, "modified": 0},
        "top_phrases": [],
        "high_risk_responses": [],
    }

    if db is not None:
        try:
            stats["total_calls"] = await db.calls.count_documents({})
            for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                stats["by_risk"][level] = await db.calls.count_documents({"risk_level": level})
            for action in ["pending", "accepted", "rejected", "modified"]:
                stats["by_action"][action] = await db.calls.count_documents({"operator_action": action})

            # Top phrases
            pipeline = [
                {"$unwind": "$phrases"},
                {"$group": {"_id": "$phrases", "count": {"$sum": 1},
                            "high_risk": {"$sum": {"$cond": [{"$in": ["$risk_level", ["HIGH", "CRITICAL"]]}, 1, 0]}}}},
                {"$sort": {"count": -1}}, {"$limit": 10},
            ]
            async for doc in db.calls.aggregate(pipeline):
                stats["top_phrases"].append({
                    "phrase": doc["_id"], "count": doc["count"],
                    "high_risk_rate": round(doc["high_risk"] / doc["count"], 2) if doc["count"] else 0,
                })

            # Best accepted responses
            pipeline2 = [
                {"$match": {"operator_action": "accepted", "risk_level": {"$in": ["HIGH", "CRITICAL"]},
                            "suggested_response": {"$ne": ""}}},
                {"$group": {"_id": "$suggested_response", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}, {"$limit": 5},
            ]
            async for doc in db.calls.aggregate(pipeline2):
                stats["high_risk_responses"].append({"response": doc["_id"], "accepted_count": doc["count"]})

            return stats
        except Exception as e:
            print(f"[learning] DB stats failed: {e}")

    # In-memory fallback
    store = get_memory_store()
    stats["total_calls"] = len(store)
    for doc in store:
        r = doc.get("risk_level", "LOW")
        if r in stats["by_risk"]:
            stats["by_risk"][r] += 1
        a = doc.get("operator_action", "pending")
        if a in stats["by_action"]:
            stats["by_action"][a] += 1
    return stats


async def generate_learning_insights() -> dict:
    """
    Use Featherless AI to generate natural language insights from call data.
    This IS the learning system — the LLM reasons over aggregated patterns.
    """
    stats = await _fetch_call_stats()

    if stats["total_calls"] == 0:
        return {
            "total_calls_analysed": 0,
            "insights": ["No call data yet. Insights will appear after calls are logged."],
            "risk_distribution": stats["by_risk"],
            "operator_response_rates": stats["by_action"],
            "top_risk_phrases": [],
            "recommended_responses": [],
            "model": MODEL,
            "powered_by": "Featherless AI",
        }

    prompt = f"""Analyse this anonymised crisis helpline call data and generate insights.

Call Statistics:
- Total calls analysed: {stats['total_calls']}
- Risk distribution: LOW={stats['by_risk']['LOW']}, MEDIUM={stats['by_risk']['MEDIUM']}, HIGH={stats['by_risk']['HIGH']}, CRITICAL={stats['by_risk']['CRITICAL']}
- Operator actions: accepted={stats['by_action']['accepted']}, rejected={stats['by_action']['rejected']}, modified={stats['by_action']['modified']}, pending={stats['by_action']['pending']}
- Top risk phrases detected: {stats['top_phrases'][:5]}
- Most accepted responses at HIGH/CRITICAL risk: {stats['high_risk_responses'][:3]}

Return JSON:
{{
  "key_insights": ["insight 1 with specific numbers", "insight 2", "insight 3"],
  "escalation_pattern": "one sentence about what predicts escalation from this data",
  "operator_trust_score": "X% of suggestions accepted — interpretation",
  "highest_risk_phrase": "the single phrase most correlated with HIGH/CRITICAL",
  "recommended_action": "one concrete recommendation for supervisors based on this data"
}}"""

    try:
        response = await _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": LEARNING_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.3,
        )
        import json, re
        content = response.choices[0].message.content or "{}"
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        match = re.search(r"\{.*\}", content, re.DOTALL)
        llm_insights = json.loads(match.group(0)) if match else {}
    except Exception as e:
        print(f"[learning] LLM insights failed: {e}")
        llm_insights = {"key_insights": ["LLM insights temporarily unavailable."]}

    total = stats["total_calls"]
    accepted = stats["by_action"]["accepted"]
    high_critical = stats["by_risk"]["HIGH"] + stats["by_risk"]["CRITICAL"]

    return {
        "total_calls_analysed": total,
        "risk_distribution": stats["by_risk"],
        "operator_response_rates": {
            "accepted": stats["by_action"]["accepted"],
            "rejected": stats["by_action"]["rejected"],
            "modified": stats["by_action"]["modified"],
            "acceptance_rate": f"{round((accepted / total) * 100)}%" if total else "0%",
        },
        "high_risk_rate": f"{round((high_critical / total) * 100)}%" if total else "0%",
        "top_risk_phrases": stats["top_phrases"][:10],
        "recommended_responses": stats["high_risk_responses"],
        "llm_insights": llm_insights,
        "model": MODEL,
        "powered_by": "Featherless AI — deepseek-ai/DeepSeek-V3-0324",
    }
