from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AgentBreakdown(BaseModel):
    language_agent: str
    emotion_agent: str
    narrative_agent: str


class RiskAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    risk_score: int = Field(ge=0, le=100)
    triggered_signals: list[str]
    agent_breakdown: AgentBreakdown
    conflict: str
    suggested_response: str
    operator_note: str
    confidence: Literal["HIGH", "MEDIUM", "LOW", "UNCERTAIN"]
