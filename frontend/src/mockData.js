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

// New detailed agent explanation data
export const MOCK_AGENT_EXPLANATION = {
  language_agent: {
    level: "HIGH",
    detected: "I've decided",
    pattern: "Finality language detected",
    confidence: 82,
  },
  emotion_agent: {
    level: "MEDIUM",
    detected: "Flat tone",
    pattern: "Low emotional variation",
    confidence: 65,
  },
  narrative_agent: {
    level: "HIGH",
    detected: "Conclusion phrasing",
    pattern: "Story reaching endpoint",
    confidence: 78,
  },
  conflict:
    "Language and Narrative agents indicate HIGH risk. Emotion agent indicates MEDIUM. Defaulting to HIGH per conservative policy.",
};

// Multi-agent conflict resolution data
export const MOCK_CONFLICT_RESOLUTION = {
  final_risk: "HIGH",
  confidence_summary: "MODERATE",
  uncertainty: true,
  explanation: `I'm flagging HIGH risk because:
• The Language Agent detected 'I've decided', 'final statements' — finality language detected
• The Narrative Agent detected 'story conclusion pattern' — narrative reaching endpoint
• The Emotion Agent detected 'flat tone' — low emotional variation

There is some uncertainty because:
• The Ambient Audio Agent did not detect strong risk signals
• Confidence levels vary significantly across agents
• Due to conflicting signals, the system is defaulting to HIGH risk as a safety measure`,
  contributing_factors: [
    "Finality language detected",
    "Narrative reaching endpoint",
    "Low emotional variation",
  ],
  conflicting_signals: [
    "Some agents indicate HIGH risk while others indicate LOW",
  ],
  agent_votes: {
    "Language Agent": "HIGH",
    "Emotion Agent": "MEDIUM",
    "Ambient Audio Agent": "LOW",
    "Narrative Agent": "HIGH",
  },
  weighted_score: 2.73,
};

// Live distress indicators data
export const MOCK_DISTRESS_INDICATORS = {
  distress_intensity: 72,
  cognitive_coherence: 45,
  agitation: 38,
  dissociation: 28,
  suicidal_ideation: 65,
  operator_fatigue: 42,
};

export const MOCK_TRANSCRIPT = [
  { time: "00:01:12", speaker: "CALLER", text: "I've been feeling really low lately.", isRisk: false },
  { time: "00:02:34", speaker: "OPERATOR", text: "Can you tell me more about that?", isRisk: false },
  { time: "00:03:45", speaker: "CALLER", text: "I've been thinking about this for weeks now.", isRisk: true },
  { time: "00:04:20", speaker: "CALLER", text: "I think I've finally decided what I need to do.", isRisk: true },
];
