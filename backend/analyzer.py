import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from mock_data import MOCK_ANALYSIS, SYSTEM_PROMPT
from models import RiskAnalysis

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("FEATHERLESS_API_KEY"),
    base_url="https://api.featherless.ai/v1",
)
MODEL_NAME = "deepseek-ai/DeepSeek-V3-0324"


def _extract_json(content: str) -> dict:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(cleaned)


async def analyze_transcript(transcript_text: str) -> RiskAnalysis:
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Transcript so far:\n{transcript_text}"},
            ],
            max_tokens=600,
            temperature=0.3,
        )
        content = response.choices[0].message.content or "{}"
        return RiskAnalysis.model_validate(_extract_json(content))
    except Exception:
        return RiskAnalysis.model_validate(
            {
                **MOCK_ANALYSIS,
                "risk_level": "HIGH",
                "risk_score": max(MOCK_ANALYSIS["risk_score"], 80),
                "confidence": "UNCERTAIN",
            }
        )
