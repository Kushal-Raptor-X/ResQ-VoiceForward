import json
import logging
import os
import re

from dotenv import load_dotenv
from openai import AsyncOpenAI

from mock_data import MOCK_ANALYSIS, SYSTEM_PROMPT
from models import MultimodalTranscript, RiskAnalysis

load_dotenv()

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=os.getenv("FEATHERLESS_API_KEY"),
    base_url="https://api.featherless.ai/v1",
)

# Use the fastest model for real-time analysis
# DeepSeek-V3 is fast and accurate for structured JSON output
MODEL_NAME = "deepseek-ai/DeepSeek-V3-0324"

logger.info(f"Featherless AI analyzer initialized with model: {MODEL_NAME}")


def _extract_json(content: str) -> dict:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(cleaned)


def _build_prosody_summary(multimodal: MultimodalTranscript) -> str:
    """Build natural language summary of prosody features."""
    if not multimodal.segments:
        return "No prosody data available."

    summary_parts = []

    # Check for unusual calm detection
    unusual_calm_segments = [
        seg for seg in multimodal.segments if seg.prosody.unusual_calm
    ]
    if unusual_calm_segments:
        summary_parts.append(
            f"UNUSUAL CALM DETECTED in {len(unusual_calm_segments)} segment(s). "
            f"This pattern (low energy + low pitch variance + slow speaking rate) "
            f"is a critical suicide risk indicator."
        )

    # Check for speaking rate changes
    if multimodal.baseline_prosody and multimodal.baseline_prosody.speaking_rate_wpm:
        baseline_rate = multimodal.baseline_prosody.speaking_rate_wpm
        recent_segments = multimodal.segments[-3:]  # Last 3 segments

        for seg in recent_segments:
            if seg.prosody.speaking_rate_wpm:
                rate_change = (
                    (seg.prosody.speaking_rate_wpm - baseline_rate) / baseline_rate * 100
                )
                if abs(rate_change) > 40:
                    summary_parts.append(
                        f"Speaking rate {'dropped' if rate_change < 0 else 'increased'} "
                        f"{abs(rate_change):.0f}% from baseline "
                        f"({baseline_rate:.0f} wpm → {seg.prosody.speaking_rate_wpm:.0f} wpm) "
                        f"at {seg.time}."
                    )

    # Report energy levels
    recent_segments = multimodal.segments[-2:]
    for seg in recent_segments:
        if seg.prosody.energy_db and seg.prosody.energy_db < -15:
            summary_parts.append(
                f"Energy level: {seg.prosody.energy_db:.1f} dB (unusually quiet) at {seg.time}."
            )

    # Report pitch variance
    if multimodal.baseline_prosody and multimodal.baseline_prosody.pitch_variance:
        baseline_var = multimodal.baseline_prosody.pitch_variance
        recent_segments = multimodal.segments[-2:]

        for seg in recent_segments:
            if seg.prosody.pitch_variance:
                var_change = baseline_var - seg.prosody.pitch_variance
                if var_change > 15:  # Significant decrease
                    summary_parts.append(
                        f"Pitch variance decreased to {seg.prosody.pitch_variance:.1f} Hz "
                        f"(baseline: {baseline_var:.1f} Hz) - indicates flat affect."
                    )

    if not summary_parts:
        return "Prosody features within normal range."

    return " ".join(summary_parts)


def _build_ambient_summary(multimodal: MultimodalTranscript) -> str:
    """Build natural language summary of ambient audio context."""
    if not multimodal.segments:
        return "No ambient audio data available."

    # Collect risk-relevant ambient classes
    risk_relevant_segments = [
        seg for seg in multimodal.segments if seg.ambient.risk_relevant
    ]

    if not risk_relevant_segments:
        return "No risk-relevant ambient audio detected."

    summary_parts = []

    # Group by primary class
    class_counts = {}
    for seg in risk_relevant_segments:
        cls = seg.ambient.primary_class
        if cls not in class_counts:
            class_counts[cls] = []
        class_counts[cls].append((seg.time, seg.ambient.confidence))

    for cls, occurrences in class_counts.items():
        avg_confidence = sum(conf for _, conf in occurrences) / len(occurrences)
        times = [time for time, _ in occurrences[:3]]  # First 3 occurrences

        summary_parts.append(
            f"{cls.replace('_', ' ').title()} detected with "
            f"{avg_confidence:.0%} confidence in segments at {', '.join(times)}."
        )

    return " ".join(summary_parts)


def _build_language_summary(multimodal: MultimodalTranscript) -> str:
    """Build natural language summary of language switching events."""
    if len(multimodal.segments) < 2:
        return "Insufficient data for language analysis."

    switches = []
    for i in range(1, len(multimodal.segments)):
        prev_lang = multimodal.segments[i - 1].language
        curr_lang = multimodal.segments[i].language

        if prev_lang != curr_lang and curr_lang != "unknown":
            switches.append(
                f"Code-switched from {prev_lang.upper()} to {curr_lang.upper()} "
                f"at {multimodal.segments[i].time}"
            )

    if not switches:
        return "No language switching detected."

    return " ".join(switches)


def _mark_risk_phrases(multimodal: MultimodalTranscript, triggered_signals: list[str]) -> None:
    """
    Parse triggered_signals for quoted phrases and mark matching segments.

    Example triggered_signal: "caller used phrase 'I've decided'"
    Extracts: "I've decided"
    Finds segments containing this phrase (case-insensitive)
    Sets isRisk=True on those segments
    """
    # Extract all quoted phrases
    risk_phrases = []
    for signal in triggered_signals:
        matches = re.findall(r"['\"]([^'\"]+)['\"]", signal)
        risk_phrases.extend(matches)

    if not risk_phrases:
        return

    logger.info(f"Marking risk phrases: {risk_phrases}")

    # Mark segments containing these phrases
    for segment in multimodal.segments:
        for phrase in risk_phrases:
            if phrase.lower() in segment.text.lower():
                segment.isRisk = True
                logger.info(f"Marked segment as risk: {segment.text}")
                break


async def analyze_transcript(multimodal: MultimodalTranscript) -> RiskAnalysis:
    """
    Analyze multimodal transcript and return risk assessment.

    Args:
        multimodal: MultimodalTranscript with text, prosody, and ambient data

    Returns:
        RiskAnalysis with triggered_signals and risk assessment
    """
    try:
        # Build text transcript
        text_transcript = "\n".join(
            [f"[{seg.time}] {seg.speaker}: {seg.text}" for seg in multimodal.segments]
        )

        # Build enriched prompt
        prosody_summary = _build_prosody_summary(multimodal)
        ambient_summary = _build_ambient_summary(multimodal)
        language_summary = _build_language_summary(multimodal)

        enriched_prompt = f"""
Transcript:
{text_transcript}

Prosody Analysis:
{prosody_summary}

Ambient Audio Context:
{ambient_summary}

Language Patterns:
{language_summary}

Analyse the above multimodal data and return risk assessment as JSON.
"""

        logger.debug(f"Enriched prompt:\n{enriched_prompt}")

        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": enriched_prompt},
            ],
            max_tokens=800,  # Increased for detailed analysis
            temperature=0.2,  # Lower for more consistent JSON output
            timeout=30.0,  # 30 second timeout for fast response
        )

        content = response.choices[0].message.content or "{}"
        analysis = RiskAnalysis.model_validate(_extract_json(content))

        # Mark risk phrases in transcript
        _mark_risk_phrases(multimodal, analysis.triggered_signals)

        return analysis

    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        return RiskAnalysis.model_validate(
            {
                **MOCK_ANALYSIS,
                "risk_level": "HIGH",
                "risk_score": max(MOCK_ANALYSIS["risk_score"], 80),
                "confidence": "UNCERTAIN",
            }
        )
