"""
Multi-agent analysis system.
Each agent independently analyses the transcript from its own lens.
The conflict resolver combines outputs into a final RiskAnalysis.
"""
import asyncio
import json
import os
import re

from dotenv import load_dotenv
from openai import AsyncOpenAI, RateLimitError

from schemas import AgentBreakdown, ResourceRecommendation, RiskAnalysis

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("FEATHERLESS_API_KEY"),
    base_url="https://api.featherless.ai/v1",
)
MODEL_NAME = "deepseek-ai/DeepSeek-V3-0324"
# Lighter model for individual agents — faster, cheaper on concurrency
AGENT_MODEL = "deepseek-ai/DeepSeek-V3-0324"

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

# Only 1 LLM call at a time — Featherless plan limit
_llm_semaphore = asyncio.Semaphore(1)

# ---------------------------------------------------------------------------
# Individual agent prompts
# ---------------------------------------------------------------------------

LANGUAGE_AGENT_PROMPT = """You are the Language Agent for a crisis helpline AI system.
Analyse ONLY the linguistic content of this transcript.
Look for: farewell language, past-tense framing, finality markers, hopelessness phrases, 
passive ideation ("everyone would be better off"), explicit ideation, closure statements.
Return JSON only:
{"verdict": "LOW|MEDIUM|HIGH|CRITICAL", "reasoning": "one sentence", "signals": ["exact quote 1", "exact quote 2"]}"""

EMOTION_AGENT_PROMPT = """You are the Emotion Agent for a crisis helpline AI system.
Analyse ONLY the emotional tone and affect in this transcript.
Look for: distress intensity, flat affect, unusual calm after distress, agitation, 
dissociation markers, emotional engagement level, tone shifts.
Return JSON only:
{"verdict": "LOW|MEDIUM|HIGH|CRITICAL", "reasoning": "one sentence", "signals": ["signal 1", "signal 2"]}"""

RISK_AGENT_PROMPT = """You are the Risk Agent for a crisis helpline AI system.
Analyse ONLY explicit and implicit suicide/self-harm risk indicators.
Look for: explicit ideation, means mentioned, timeline mentioned, plan indicators (letters written, 
giving away possessions), access to means, previous attempts mentioned.
Return JSON only:
{"verdict": "LOW|MEDIUM|HIGH|CRITICAL", "reasoning": "one sentence", "signals": ["signal 1", "signal 2"]}"""

CONTEXT_AGENT_PROMPT = """You are the Context Agent for a crisis helpline AI system.
Analyse the CONVERSATION PATTERN and escalation trajectory.
Look for: escalation across turns, disclosure deepening, topic shifts toward risk, 
narrative arc (has the caller reached a conclusion?), rapport level, call duration context.
Return JSON only:
{"verdict": "LOW|MEDIUM|HIGH|CRITICAL", "reasoning": "one sentence", "signals": ["signal 1", "signal 2"]}"""

RESOLVER_PROMPT = """You are the Conflict Resolution Engine for a crisis helpline AI system.
You receive outputs from 4 independent agents. Combine them into a final risk assessment.
Rules:
- ALWAYS escalate to the highest risk level when agents disagree
- If signals are contradictory, set confidence to UNCERTAIN
- Flat affect / unusual calm is itself a HIGH indicator, not a LOW one
- triggered_signals must quote ACTUAL WORDS from the transcript
- suggested_response must be warm, human, non-clinical, max 2 sentences
- conflict_resolution must explain WHY you chose the final level
- resources must be ranked by priority for this specific situation

Return ONLY valid JSON, no markdown, no preamble:
{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "risk_score": 0-100,
  "triggered_signals": ["exact quote or pattern"],
  "conflict": "one sentence describing agent disagreement if any",
  "conflict_resolution": "one sentence explaining final decision rationale",
  "suggested_response": "warm operator response",
  "operator_note": "brief tactical note for operator",
  "confidence": "HIGH|MEDIUM|LOW|UNCERTAIN",
  "resources": [
    {"label": "resource name", "action": "action description", "priority": "HIGH|MEDIUM|LOW"}
  ]
}"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json(content: str) -> dict:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    # Extract the first complete JSON object
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to salvage truncated JSON by closing open structures
        try:
            # Count unclosed braces/brackets and close them
            open_braces = cleaned.count("{") - cleaned.count("}")
            open_brackets = cleaned.count("[") - cleaned.count("]")
            salvaged = cleaned.rstrip(",\n ") + ("]" * open_brackets) + ("}" * open_braces)
            return json.loads(salvaged)
        except Exception:
            return {}


async def _call_llm(system: str, user: str, max_tokens: int = 400) -> dict:
    """Call LLM with retry on rate limit (max 3 attempts, 5s backoff)."""
    async with _llm_semaphore:
        for attempt in range(3):
            try:
                response = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    max_tokens=max_tokens,
                    temperature=0.2,
                )
                return _parse_json(response.choices[0].message.content or "{}")
            except RateLimitError:
                if attempt < 2:
                    await asyncio.sleep(6 + attempt * 4)  # 6s, 10s backoff
                else:
                    raise
            except Exception:
                raise


# ---------------------------------------------------------------------------
# Individual agents
# ---------------------------------------------------------------------------

async def run_language_agent(transcript: str) -> dict:
    try:
        return await _call_llm(LANGUAGE_AGENT_PROMPT, f"Transcript:\n{transcript}")
    except Exception:
        return {"verdict": "UNCERTAIN", "reasoning": "Language agent unavailable.", "signals": []}


async def run_emotion_agent(transcript: str) -> dict:
    try:
        return await _call_llm(EMOTION_AGENT_PROMPT, f"Transcript:\n{transcript}")
    except Exception:
        return {"verdict": "UNCERTAIN", "reasoning": "Emotion agent unavailable.", "signals": []}


async def run_risk_agent(transcript: str) -> dict:
    try:
        return await _call_llm(RISK_AGENT_PROMPT, f"Transcript:\n{transcript}")
    except Exception:
        return {"verdict": "UNCERTAIN", "reasoning": "Risk agent unavailable.", "signals": []}


async def run_context_agent(transcript: str) -> dict:
    try:
        return await _call_llm(CONTEXT_AGENT_PROMPT, f"Transcript:\n{transcript}")
    except Exception:
        return {"verdict": "UNCERTAIN", "reasoning": "Context agent unavailable.", "signals": []}


# ---------------------------------------------------------------------------
# Conflict resolver
# ---------------------------------------------------------------------------

async def resolve_conflict(
    transcript: str,
    language: dict,
    emotion: dict,
    risk: dict,
    context: dict,
) -> RiskAnalysis:
    agent_summary = (
        f"Language Agent: {language.get('verdict')} — {language.get('reasoning')}\n"
        f"Emotion Agent: {emotion.get('verdict')} — {emotion.get('reasoning')}\n"
        f"Risk Agent: {risk.get('verdict')} — {risk.get('reasoning')}\n"
        f"Context Agent: {context.get('verdict')} — {context.get('reasoning')}\n\n"
        f"All signals:\n"
        + "\n".join(
            f"- {s}"
            for s in (
                language.get("signals", [])
                + emotion.get("signals", [])
                + risk.get("signals", [])
                + context.get("signals", [])
            )
        )
        + f"\n\nOriginal transcript:\n{transcript}"
    )

    result = await _call_llm(RESOLVER_PROMPT, agent_summary, max_tokens=700)

    # Sanitise risk_level — LLM sometimes returns UNCERTAIN which is not valid
    raw_risk = result.get("risk_level", "HIGH").upper()
    if raw_risk not in RISK_ORDER:
        raw_risk = "HIGH"  # conservative default

    # Sanitise confidence
    raw_conf = result.get("confidence", "UNCERTAIN").upper()
    if raw_conf not in ("HIGH", "MEDIUM", "LOW", "UNCERTAIN"):
        raw_conf = "UNCERTAIN"

    # Sanitise risk_score
    try:
        raw_score = max(0, min(100, int(result.get("risk_score", 75))))
    except (TypeError, ValueError):
        raw_score = 75

    # Build AgentBreakdown strings
    breakdown = AgentBreakdown(
        language_agent=f"{language.get('verdict', 'UNCERTAIN')} - {language.get('reasoning', 'No data')}",
        emotion_agent=f"{emotion.get('verdict', 'UNCERTAIN')} - {emotion.get('reasoning', 'No data')}",
        risk_agent=f"{risk.get('verdict', 'UNCERTAIN')} - {risk.get('reasoning', 'No data')}",
        context_agent=f"{context.get('verdict', 'UNCERTAIN')} - {context.get('reasoning', 'No data')}",
    )

    resources = [
        ResourceRecommendation(**r)
        for r in result.get("resources", [])
        if isinstance(r, dict) and all(k in r for k in ("label", "action", "priority"))
        and r.get("priority") in ("HIGH", "MEDIUM", "LOW")
    ]

    return RiskAnalysis(
        risk_level=raw_risk,
        risk_score=raw_score,
        triggered_signals=result.get("triggered_signals", []),
        agent_breakdown=breakdown,
        conflict=result.get("conflict", ""),
        conflict_resolution=result.get("conflict_resolution", ""),
        suggested_response=result.get("suggested_response", ""),
        operator_note=result.get("operator_note", ""),
        confidence=raw_conf,
        resources=resources,
        ambient_signals=[],
        operator_fatigue_flag=False,
        failure_mode=None,
    )
