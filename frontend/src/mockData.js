export const MOCK_ANALYSIS = {
  risk_level: "HIGH",
  risk_score: 78,
  triggered_signals: [
    "caller used phrase 'I've decided'",
    "speaking pace dropped significantly",
    "unusual calm tone detected",
  ],
  agent_breakdown: {
    language_agent: "HIGH - passive farewell language detected",
    emotion_agent: "MEDIUM - flat affect, minimal emotional variation",
    narrative_agent: "HIGH - story reached a conclusion point",
  },
  conflict:
    "Language and narrative agents flag HIGH. Emotion agent flags MEDIUM. Defaulting to HIGH per conservative protocol.",
  suggested_response:
    "It sounds like you've been carrying this for a long time. Can you tell me what today felt like?",
  operator_note:
    "Do not rush. Caller appears to have made a decision. Keep them talking.",
  confidence: "HIGH",
};

export const MOCK_TRANSCRIPT = [
  { time: "00:01:12", speaker: "CALLER", text: "I've been feeling really low lately.", isRisk: false },
  { time: "00:02:34", speaker: "OPERATOR", text: "Can you tell me more about that?", isRisk: false },
  { time: "00:03:45", speaker: "CALLER", text: "I've been thinking about this for weeks now.", isRisk: true },
  { time: "00:04:20", speaker: "CALLER", text: "I think I've finally decided what I need to do.", isRisk: true },
];
