from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentBreakdown(BaseModel):
    language_agent: str
    emotion_agent: str
    risk_agent: str
    context_agent: str


class ResourceRecommendation(BaseModel):
    label: str
    action: str
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    used: bool = False


class RiskAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    risk_score: int = Field(ge=0, le=100)
    triggered_signals: list[str]
    agent_breakdown: AgentBreakdown
    conflict: str
    conflict_resolution: str
    suggested_response: str
    operator_note: str
    confidence: Literal["HIGH", "MEDIUM", "LOW", "UNCERTAIN"]
    resources: list[ResourceRecommendation] = Field(default_factory=list)
    ambient_signals: list[str] = Field(default_factory=list)
    operator_fatigue_flag: bool = False
    failure_mode: Optional[str] = None


class OperatorActionLog(BaseModel):
    sid: str
    action: Literal["ACCEPT", "MODIFY", "REJECT"]
    suggestion: str
    risk_level: str
    risk_score: int
    confidence: str
    reasoning: str
    timestamp: str
    resource_used: Optional[str] = None


# ---------------------------------------------------------------------------
# /analyze endpoint models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    transcript: str
    session_id: Optional[str] = None   # caller session — no PII


class AgentResult(BaseModel):
    verdict: str
    reasoning: str
    signals: list[str]


class AnalyzeInsights(BaseModel):
    similar_case_risk: str
    best_response_success: str
    data_note: str


class AnalyzeResponse(BaseModel):
    session_id: str
    risk: str
    risk_score: int
    confidence: float                  # 0.0–1.0 numeric
    confidence_label: str              # HIGH | MEDIUM | LOW | UNCERTAIN
    reasoning: list[str]               # human-readable reasoning array
    triggered_signals: list[str]
    agent_breakdown: dict              # per-agent verdict + reasoning
    conflict: str
    conflict_resolution: str
    suggested_response: str
    operator_note: str
    resources: list[dict]
    insights: AnalyzeInsights
    warnings: list[str]                # Layer 5: uncertainty / failure warnings
    record_id: Optional[str] = None   # MongoDB document ID for action update

