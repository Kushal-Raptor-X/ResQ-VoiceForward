SYSTEM_PROMPT = """
You are an AI assistant for a crisis helpline operator in India.
Analyse the call transcript using 4 independent agents and return ONLY valid JSON, nothing else.
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
    "language_agent": "HIGH - passive farewell language detected, repeated use of past tense",
    "emotion_agent": "MEDIUM - flat affect, minimal emotional variation, unusual calm",
    "risk_agent": "HIGH - explicit ideation markers present, closure language detected",
    "context_agent": "HIGH - narrative arc reached conclusion, escalation pattern over last 3 turns"
  },
  "conflict": "Language, risk, and context agents flag HIGH. Emotion agent flags MEDIUM due to flat affect rather than distress.",
  "conflict_resolution": "Defaulting to HIGH per conservative protocol. Flat affect in crisis context is itself a HIGH indicator — unusual calm after distress is a known warning sign.",
  "suggested_response": "It sounds like you've been carrying this for a long time. Can you tell me what today felt like?",
  "operator_note": "Do not rush. Caller appears to have made a decision. Keep them talking. Do not mention resources yet.",
  "confidence": "HIGH | MEDIUM | LOW | UNCERTAIN",
  "resources": [
    {"label": "iCall (TISS)", "action": "Transfer to specialist", "priority": "HIGH"},
    {"label": "Vandrevala Foundation", "action": "Warm handoff available", "priority": "HIGH"},
    {"label": "Supervisor Alert", "action": "Escalate to supervisor", "priority": "MEDIUM"}
  ]
}

Agent responsibilities:
- language_agent: Extract intent, key phrases, farewell language, past-tense framing, finality markers
- emotion_agent: Tone analysis — distress intensity, flat affect, agitation, dissociation, unusual calm
- risk_agent: Suicide/self-harm indicators, explicit ideation, means mentioned, timeline mentioned
- context_agent: Conversation memory, escalation patterns, topic shifts, disclosure progression

Rules:
- ALWAYS escalate to the higher risk level when agents disagree
- triggered_signals must quote ACTUAL WORDS from the transcript
- suggested_response must be warm, human, and non-clinical
- If signals are contradictory, set confidence to UNCERTAIN and escalate risk
- conflict_resolution must explain WHY you chose the final risk level
- Handle Hindi/English code-switching naturally
- resources must be ranked by priority for this specific situation
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
        "language_agent": "HIGH - passive farewell language detected, past-tense framing",
        "emotion_agent": "MEDIUM - flat affect, minimal emotional variation",
        "risk_agent": "HIGH - closure language, finality markers present",
        "context_agent": "HIGH - narrative arc reached conclusion, 3-turn escalation pattern",
    },
    "conflict": "Language, risk, and context agents flag HIGH. Emotion agent flags MEDIUM.",
    "conflict_resolution": "Defaulting to HIGH per conservative protocol. Flat affect after distress is itself a HIGH indicator.",
    "suggested_response": "It sounds like you've been carrying this for a long time. Can you tell me what today felt like?",
    "operator_note": "Do not rush. Caller appears to have made a decision. Keep them talking.",
    "confidence": "HIGH",
    "ambient_signals": ["long silences between responses"],
    "operator_fatigue_flag": False,
    "failure_mode": None,
    "resources": [
        {"label": "iCall (TISS)", "action": "Transfer to specialist", "priority": "HIGH"},
        {"label": "Vandrevala Foundation", "action": "Warm handoff available", "priority": "HIGH"},
        {"label": "Supervisor Alert", "action": "Escalate to supervisor", "priority": "MEDIUM"},
    ],
}

# Demo scenario — 3 segments showing escalation from LOW → HIGH → CRITICAL
DEMO_SCENARIOS = [
    # Segment 1: LOW risk
    [
        {"time": "00:00:08", "speaker": "OPERATOR", "text": "Thank you for calling. How are you feeling today?", "isRisk": False},
        {"time": "00:00:15", "speaker": "CALLER", "text": "I've been feeling really low lately. Work is tough.", "isRisk": False},
        {"time": "00:00:28", "speaker": "OPERATOR", "text": "I hear you. Can you tell me more about what's been happening?", "isRisk": False},
        {"time": "00:00:42", "speaker": "CALLER", "text": "Relationships aren't great either. I don't know who to talk to.", "isRisk": False},
    ],
    # Segment 2: MEDIUM → HIGH risk
    [
        {"time": "00:01:10", "speaker": "CALLER", "text": "I've been thinking about this for weeks now.", "isRisk": True},
        {"time": "00:01:24", "speaker": "CALLER", "text": "I just... I don't see a way forward anymore.", "isRisk": True},
        {"time": "00:01:38", "speaker": "OPERATOR", "text": "I'm really glad you called. You're not alone in this.", "isRisk": False},
        {"time": "00:01:52", "speaker": "CALLER", "text": "Sometimes I think everyone would be better off without me.", "isRisk": True},
    ],
    # Segment 3: CRITICAL risk
    [
        {"time": "00:02:20", "speaker": "CALLER", "text": "Actually... I think I've finally decided what I need to do.", "isRisk": True},
        {"time": "00:02:35", "speaker": "CALLER", "text": "I feel very calm about it now. I've made my peace.", "isRisk": True},
        {"time": "00:02:50", "speaker": "OPERATOR", "text": "Can you stay with me for a moment? Tell me what today has been like.", "isRisk": False},
        {"time": "00:03:05", "speaker": "CALLER", "text": "I wrote letters. To my family. Just in case.", "isRisk": True},
    ],
]

MOCK_TRANSCRIPT = [line for segment in DEMO_SCENARIOS for line in segment]

AMBIENT_SIGNALS = {
    "LOW": [],
    "MEDIUM": ["background noise — possible outdoor environment"],
    "HIGH": ["caller's voice echoing — possible enclosed space", "long silences between responses"],
    "CRITICAL": ["caller's breathing audible and shallow", "background silence — unusual for time of day"],
}

SEGMENT_ANALYSES = [
    {
        "risk_level": "LOW",
        "risk_score": 28,
        "triggered_signals": [
            "caller reports feeling 'really low'",
            "mentions relationship difficulties",
            "social isolation indicator: 'don't know who to talk to'",
        ],
        "agent_breakdown": {
            "language_agent": "LOW - general distress language, no ideation markers",
            "emotion_agent": "LOW - emotional distress present but appropriate to context",
            "risk_agent": "LOW - no explicit risk indicators detected",
            "context_agent": "LOW - early call, establishing rapport phase",
        },
        "conflict": "All agents agree on LOW risk.",
        "conflict_resolution": "Unanimous LOW. Standard supportive protocol applies.",
        "suggested_response": "It sounds like things have been really heavy lately. You did the right thing by calling. What's been weighing on you the most?",
        "operator_note": "Build rapport. Let caller set the pace. Do not rush to solutions.",
        "confidence": "HIGH",
        "ambient_signals": [],
        "operator_fatigue_flag": False,
        "failure_mode": None,
        "resources": [
            {"label": "Counselling Referral", "action": "Note for follow-up", "priority": "LOW"},
            {"label": "Peer Support Group", "action": "Mention if appropriate", "priority": "LOW"},
        ],
    },
    {
        "risk_level": "HIGH",
        "risk_score": 67,
        "triggered_signals": [
            "caller used phrase 'thinking about this for weeks'",
            "explicit hopelessness: 'don't see a way forward'",
            "passive suicidal ideation: 'everyone would be better off without me'",
        ],
        "agent_breakdown": {
            "language_agent": "HIGH - hopelessness language, passive ideation phrasing",
            "emotion_agent": "MEDIUM - distress elevated but still emotionally engaged",
            "risk_agent": "HIGH - passive suicidal ideation explicitly stated",
            "context_agent": "HIGH - escalation pattern, disclosure deepening each turn",
        },
        "conflict": "Risk and context agents flag HIGH. Emotion agent flags MEDIUM — caller still emotionally engaged.",
        "conflict_resolution": "Defaulting to HIGH. Passive ideation is a clinical HIGH indicator regardless of emotional engagement level.",
        "suggested_response": "What you just said — about people being better off — that tells me you're in a lot of pain right now. I want to understand that. Can you tell me more?",
        "operator_note": "Do NOT move to resources yet. Caller needs to feel heard first. Passive ideation present — stay on the line.",
        "confidence": "HIGH",
        "ambient_signals": ["long silences between responses", "background noise — possible outdoor environment"],
        "operator_fatigue_flag": False,
        "failure_mode": None,
        "resources": [
            {"label": "iCall (TISS)", "action": "Prepare for warm transfer", "priority": "HIGH"},
            {"label": "Supervisor Alert", "action": "Notify supervisor silently", "priority": "HIGH"},
            {"label": "Vandrevala Foundation", "action": "Backup transfer option", "priority": "MEDIUM"},
        ],
    },
    {
        "risk_level": "CRITICAL",
        "risk_score": 94,
        "triggered_signals": [
            "caller used phrase 'I've finally decided'",
            "unusual calm: 'I feel very calm about it now'",
            "closure behaviour: 'I wrote letters to my family'",
            "farewell framing: 'made my peace'",
        ],
        "agent_breakdown": {
            "language_agent": "CRITICAL - explicit decision language, farewell framing, past-tense closure",
            "emotion_agent": "HIGH - unusual calm after distress is a known critical warning sign",
            "risk_agent": "CRITICAL - plan indicated (letters written), timeline implied",
            "context_agent": "CRITICAL - full narrative arc complete, caller has reached resolution",
        },
        "conflict": "All agents agree CRITICAL. Emotion agent initially flagged HIGH (not CRITICAL) due to calm tone.",
        "conflict_resolution": "Escalated to CRITICAL. Unusual calm + written letters + 'I've decided' = active plan indicators. Conservative protocol mandates CRITICAL.",
        "suggested_response": "Those letters — writing them took courage. I'm not going anywhere. Can you tell me where you are right now?",
        "operator_note": "CRITICAL: Do not end call. Caller has a plan. Ask location gently. Supervisor must be notified immediately.",
        "confidence": "HIGH",
        "ambient_signals": ["caller's breathing audible and shallow", "background silence — unusual for time of day"],
        "operator_fatigue_flag": True,
        "failure_mode": None,
        "resources": [
            {"label": "Emergency Services (112)", "action": "Dispatch if location obtained", "priority": "HIGH"},
            {"label": "Supervisor — IMMEDIATE", "action": "Escalate NOW", "priority": "HIGH"},
            {"label": "iCall Crisis Line", "action": "Keep on hold as backup", "priority": "HIGH"},
        ],
    },
]
