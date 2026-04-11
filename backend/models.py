from typing import Literal, Optional

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


# Multimodal data structures for Layer 1


class WordTimestamp(BaseModel):
    """Individual word with timing and confidence."""

    word: str
    start: float  # seconds from chunk start
    end: float
    confidence: float = Field(ge=0.0, le=1.0)


class ProsodyFeatures(BaseModel):
    """Paralinguistic features extracted from audio."""

    speaking_rate_wpm: Optional[float] = None
    pitch_mean_hz: Optional[float] = None
    pitch_variance: Optional[float] = None
    energy_db: Optional[float] = None
    pause_ratio: Optional[float] = None
    pitch_trend: Literal["rising", "falling", "stable", "unknown"] = "unknown"
    unusual_calm: bool = False


class AmbientAudio(BaseModel):
    """Background audio classification."""

    primary_class: Literal[
        "child_crying", "silence", "traffic", "music", "multiple_speakers", "unknown"
    ] = "unknown"
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    secondary_classes: list[str] = Field(default_factory=list)
    risk_relevant: bool = False


class TranscriptSegment(BaseModel):
    """Single utterance with all modalities."""

    time: str  # "00:03:45" format
    speaker: Literal["CALLER", "OPERATOR", "SYSTEM"]
    text: str
    words: list[WordTimestamp] = Field(default_factory=list)
    language: Literal["en", "hi", "unknown"] = "unknown"
    prosody: ProsodyFeatures = Field(default_factory=ProsodyFeatures)
    ambient: AmbientAudio = Field(default_factory=AmbientAudio)
    isRisk: bool = False  # Set by LLM analysis


class MultimodalTranscript(BaseModel):
    """Complete call session with all segments."""

    segments: list[TranscriptSegment] = Field(default_factory=list)
    call_duration_sec: float = 0.0
    total_caller_speech_sec: float = 0.0
    total_operator_speech_sec: float = 0.0
    baseline_prosody: Optional[ProsodyFeatures] = None  # Computed from first 60s

    def add_segment(self, segment: TranscriptSegment) -> None:
        """Add segment and update duration counters."""
        self.segments.append(segment)
        # Update speech duration counters based on speaker
        # (Implementation can be added later if needed)

    def get_recent_context(self, seconds: int = 30) -> str:
        """Get last N seconds of transcript text for Whisper context."""
        if not self.segments:
            return ""

        # Simple implementation: return last N segments
        # (Could be improved to use actual timestamps)
        recent_segments = self.segments[-5:]  # Last 5 segments as approximation
        return " ".join(seg.text for seg in recent_segments)
