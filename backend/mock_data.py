SYSTEM_PROMPT = """
You are an AI assistant for a crisis helpline operator in India.
Analyse the call transcript and return ONLY valid JSON, nothing else.
No preamble. No markdown. Raw JSON only.

{
  "risk_level": "LOW | MEDIUM | HIGH | CRITICAL",
  "risk_score": 0-100,
  "triggered_signals": [
    "caller used phrase 'I've decided'",
    "speaking pace dropped significantly",
    "unusual calm tone detected"
  ],
  "agent_breakdown": {
    "language_agent": "HIGH - passive farewell language detected",
    "emotion_agent": "MEDIUM - flat affect, minimal emotional variation",
    "narrative_agent": "HIGH - story reached a conclusion point"
  },
  "conflict": "Language and narrative agents flag HIGH. Emotion agent flags MEDIUM. Defaulting to HIGH per conservative protocol.",
  "suggested_response": "It sounds like you've been carrying this for a long time. Can you tell me what today felt like?",
  "operator_note": "Do not rush. Caller appears to have made a decision. Keep them talking.",
  "confidence": "HIGH | MEDIUM | LOW | UNCERTAIN"
}

Rules:
- ALWAYS escalate to the higher risk level when agents disagree
- triggered_signals must quote ACTUAL WORDS from the transcript
- suggested_response must be warm, human, and non-clinical
- If signals are contradictory, set confidence to UNCERTAIN and escalate risk
- Handle Hindi/English code-switching naturally
"""

MOCK_ANALYSIS = {
    "risk_level": "HIGH",
    "risk_score": 78,
    "triggered_signals": [
        "caller used phrase 'I've decided'",
        "speaking pace dropped significantly",
        "unusual calm tone detected",
    ],
    "agent_breakdown": {
        "language_agent": "HIGH - passive farewell language detected",
        "emotion_agent": "MEDIUM - flat affect, minimal emotional variation",
        "narrative_agent": "HIGH - story reached a conclusion point",
    },
    "conflict": (
        "Language and narrative agents flag HIGH. Emotion agent flags MEDIUM. "
        "Defaulting to HIGH per conservative protocol."
    ),
    "suggested_response": (
        "It sounds like you've been carrying this for a long time. "
        "Can you tell me what today felt like?"
    ),
    "operator_note": (
        "Do not rush. Caller appears to have made a decision. Keep them talking."
    ),
    "confidence": "HIGH",
}

MOCK_TRANSCRIPT = [
    {"time": "00:01:12", "speaker": "CALLER", "text": "I've been feeling really low lately.", "isRisk": False},
    {"time": "00:02:34", "speaker": "OPERATOR", "text": "Can you tell me more about that?", "isRisk": False},
    {"time": "00:03:45", "speaker": "CALLER", "text": "I've been thinking about this for weeks now.", "isRisk": True},
    {"time": "00:04:20", "speaker": "CALLER", "text": "I think I've finally decided what I need to do.", "isRisk": True},
]
