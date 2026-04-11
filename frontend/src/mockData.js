export const MOCK_ANALYSIS = {
  risk_level: "HIGH",
  risk_score: 78,
  triggered_signals: [
    "caller used phrase 'I've decided'",
    "speaking pace dropped significantly",
    "unusual calm tone detected",
  ],
  agent_breakdown: {
    language_agent: "HIGH - passive farewell language detected, past-tense framing",
    emotion_agent: "MEDIUM - flat affect, minimal emotional variation",
    risk_agent: "HIGH - closure language, finality markers present",
    context_agent: "HIGH - narrative arc reached conclusion, 3-turn escalation pattern",
  },
  conflict: "Language, risk, and context agents flag HIGH. Emotion agent flags MEDIUM.",
  conflict_resolution:
    "Defaulting to HIGH per conservative protocol. Flat affect after distress is itself a HIGH indicator.",
  suggested_response:
    "It sounds like you've been carrying this for a long time. Can you tell me what today felt like?",
  operator_note: "Do not rush. Caller appears to have made a decision. Keep them talking.",
  confidence: "HIGH",
  ambient_signals: ["long silences between responses"],
  operator_fatigue_flag: false,
  failure_mode: null,
  resources: [
    { label: "iCall (TISS)", action: "Transfer to specialist", priority: "HIGH" },
    { label: "Vandrevala Foundation", action: "Warm handoff available", priority: "HIGH" },
    { label: "Supervisor Alert", action: "Escalate to supervisor", priority: "MEDIUM" },
  ],
};

export const MOCK_TRANSCRIPT = [
  { time: "00:00:15", speaker: "CALLER", text: "I've been feeling really low lately. Work is tough.", isRisk: false },
  { time: "00:00:42", speaker: "CALLER", text: "Relationships aren't great either. I don't know who to talk to.", isRisk: false },
  { time: "00:01:10", speaker: "CALLER", text: "I've been thinking about this for weeks now.", isRisk: true },
  { time: "00:01:52", speaker: "CALLER", text: "Sometimes I think everyone would be better off without me.", isRisk: true },
  { time: "00:02:20", speaker: "CALLER", text: "Actually... I think I've finally decided what I need to do.", isRisk: true },
  { time: "00:02:35", speaker: "CALLER", text: "I feel very calm about it now. I've made my peace.", isRisk: true },
  { time: "00:03:05", speaker: "CALLER", text: "I wrote letters. To my family. Just in case.", isRisk: true },
];
