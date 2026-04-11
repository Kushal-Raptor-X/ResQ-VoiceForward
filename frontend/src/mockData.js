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
  { time: "00:00:10", speaker: "CALLER", text: "Hi, I've been feeling really low lately. Work is tough, relationships aren't great. I don't know who to talk to.", isRisk: false },
  { time: "00:00:18", speaker: "OPERATOR", text: "I'm here to listen. Can you tell me more about what's been happening?", isRisk: false },
  { time: "00:00:30", speaker: "CALLER", text: "I've been thinking about this for weeks now. I just... I don't see a way forward anymore.", isRisk: true },
  { time: "00:00:40", speaker: "OPERATOR", text: "That sounds really difficult. What does 'a way forward' mean to you?", isRisk: false },
  { time: "00:00:55", speaker: "CALLER", text: "Actually... I think I've finally decided what I need to do. I feel very calm about it now.", isRisk: true },
  { time: "00:01:05", speaker: "OPERATOR", text: "Can you tell me more about what you've decided?", isRisk: false },
];
