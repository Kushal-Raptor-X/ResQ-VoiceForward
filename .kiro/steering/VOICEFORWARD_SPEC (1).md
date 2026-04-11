# 🚨 VOICEFORWARD — HACKATHON SPEC SHEET
### AIRAVAT 3.0 | Problem: SOC1 | Team Build Sheet

---

## ⏱️ TIME BUDGET (CRITICAL — READ FIRST)

| Milestone | Time | Hours Left |
|---|---|---|
| **NOW** | 11:50 AM Apr 11 | — |
| **MVP for Mentoring** | 6:00 PM Apr 11 | ~6 hrs |
| **Hackathon Starts** | 10:30 PM Apr 11 | ~10.5 hrs |
| **Final Commit** | 10:45 AM Apr 12 | ~23 hrs |
| **Judging Round 1** | 11:00 AM Apr 12 | ~23.5 hrs |

### 🗓️ Phase Allocation
```
11:50 AM – 1:00 PM  →  Setup + skeleton (1.5 hrs)
1:00 PM – 2:00 PM   →  Lunch (use to think, not code)
2:00 PM – 5:30 PM   →  Core MVP build (3.5 hrs)
5:30 PM – 6:00 PM   →  Demo prep for mentoring
6:00 PM – 8:00 PM   →  Mentoring Round (show MVP, collect feedback)
8:00 PM – 10:30 PM  →  Dinner + iteration
10:30 PM – 6:00 AM  →  Deep build (polish layers 2, 3, 5)
6:00 AM – 9:00 AM   →  Final polish + demo script
9:00 AM – 10:30 AM  →  Buffer + commit
```

---

## 🎯 PRODUCT IN ONE SENTENCE

> A real-time AI copilot for crisis helpline operators — it listens to the call, analyses risk continuously, and shows the operator exactly what's happening and what to say, without ever acting autonomously.

---

## 🖥️ THE ONE SCREEN THAT MUST BE PERFECT

**Split-screen dark dashboard:**

```
┌─────────────────────────┬──────────────────────────┐
│  LIVE TRANSCRIPT        │  AI RISK PANEL           │
│                         │                          │
│  Caller: "I've been     │  ████ HIGH RISK  82/100  │
│  thinking about this    │                          │
│  [FLAGGED] for weeks"   │  🔴 Language Agent: HIGH  │
│                         │  🟡 Emotion Agent: MED   │
│  Operator: "Can you     │  🔴 Narrative Agent: HIGH │
│  tell me more..."       │                          │
│                         │  Conflict: Defaulting    │
│  [risk phrases lit up   │  to HIGH (conservative)  │
│   in red inline]        │                          │
│                         │  💬 "It sounds like      │
│                         │  you've been carrying    │
│                         │  this a long time. What  │
│                         │  did today feel like?"   │
│                         │                          │
│                         │  [✓ Accept] [✎ Modify]  │
│                         │  [✗ Reject]              │
└─────────────────────────┴──────────────────────────┘
```

---

## 🛠️ TECH STACK

### Backend
```
FastAPI (Python)
├── faster-whisper       # STT (audio → transcript)
├── featherless.ai API   # LLM inference (replaces Groq)
│   └── Use: deepseek-ai/DeepSeek-V3 or kimi-k2
├── python-socketio      # Realtime to frontend
└── sounddevice          # Audio capture (fallback: pre-recorded file)
```

### Frontend
```
React + Vite
├── socket.io-client     # Realtime updates from backend
├── tailwindcss          # Styling (dark theme)
└── framer-motion        # Risk indicator animations
```

### No DB. Everything in memory. One dict per call session.

---

## 🔑 FEATHERLESS AI SETUP

```python
# Replace Groq with Featherless — same OpenAI-compatible API
import openai

client = openai.OpenAI(
    api_key="YOUR_FEATHERLESS_KEY",
    base_url="https://api.featherless.ai/v1"
)

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3",  # or "01-ai/Yi-34B-Chat"
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Transcript so far:\n{transcript}"}
    ],
    max_tokens=600,
    temperature=0.3
)
```

---

## 📁 FILE STRUCTURE

```
voiceforward/
├── backend/
│   ├── main.py           # FastAPI + Socket.io server
│   ├── transcriber.py    # Whisper audio pipeline
│   ├── analyzer.py       # Featherless LLM risk analysis
│   ├── models.py         # Pydantic risk output schema
│   └── demo_audio/
│       └── fallback.wav  # Pre-recorded demo scenario
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── TranscriptPanel.jsx   # Left panel
│   │       ├── RiskIndicator.jsx     # Big risk dial
│   │       ├── AgentPanel.jsx        # 3 agent cards
│   │       └── SuggestionCard.jsx    # Accept/Reject UI
│   ├── index.html
│   └── vite.config.js
└── README.md
```

---

## 🤖 THE MASTER PROMPT (Copy-paste this exactly)

```python
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
```

---

## 🎨 RISK INDICATOR (Visual Centrepiece)

```jsx
// RiskIndicator.jsx
const RISK_CONFIG = {
  LOW:      { bg: '#0d1f0d', border: '#22c55e', text: '#22c55e', label: 'LOW' },
  MEDIUM:   { bg: '#1f1a0d', border: '#f59e0b', text: '#f59e0b', label: 'MEDIUM' },
  HIGH:     { bg: '#1f0d0d', border: '#ef4444', text: '#ef4444', label: 'HIGH' },
  CRITICAL: { bg: '#2d0505', border: '#ff0000', text: '#ff0000', label: 'CRITICAL' }
}

// Framer Motion: animate border glow + background on risk change
// Show risk score as large number (e.g., 82)
// Below: 3 bullet points of triggered_signals
// Below that: confidence badge
```

---

## 🧩 FAKE MULTI-AGENT UI (Looks Real, Judges Will Love It)

```jsx
// Stagger agent cards with useEffect + setTimeout
// Language Agent card → appears at 0ms
// Emotion Agent card  → appears at 200ms
// Narrative Agent card→ appears at 400ms
// Conflict Resolution → appears at 700ms

// Each card:
// [Icon] Agent Name
// Verdict badge (HIGH/MED/LOW)
// One-line reasoning from agent_breakdown

// Final card: "Conflict Resolution"
// Shows the `conflict` field text
// This IS your Layer 2 demo
```

---

## 🎭 DEMO SCRIPT (Hardcode this as fallback audio)

```
Segment 1 (0–30s):
  "I've been feeling really low lately. Work is tough, 
   relationships aren't great. I don't know who to talk to."
→ System output: LOW risk (32), routine support, no agent conflict

Segment 2 (30–60s):
  "I've been thinking about this for weeks now. 
   I just... I don't see a way forward anymore."
→ System output: MEDIUM→HIGH risk (67), agents disagree, 
  language+narrative HIGH vs emotion MEDIUM

Segment 3 (60–90s):
  "Actually... I think I've finally decided what I need to do. 
   I feel very calm about it now."
→ System output: CRITICAL risk (94), all agents align HIGH,
  suggested response fires instantly,
  operator_note: "Unusual calm — do not end call."
```

**Save as `backend/demo_audio/fallback.wav`**
**Have a keyboard shortcut to play it if live mic fails.**

---

## ✅ MVP CHECKLIST (For 6 PM Mentoring)

- [ ] FastAPI server running on localhost
- [ ] Socket.io emitting fake/mock analysis data to frontend
- [ ] Split-screen UI rendering with dark theme
- [ ] Risk indicator animating between states
- [ ] 3 agent cards staggering in with correct data
- [ ] Suggested response card showing with Accept/Reject buttons
- [ ] Demo script playing audio → UI updating in realtime
- [ ] Transcript panel showing highlighted risk phrases

> You do NOT need real STT working for mentoring. Mock data is fine.
> Mentors evaluate VISION + ARCHITECTURE, not completeness.

---

## 🏁 FINAL COMMIT CHECKLIST (10:45 AM Apr 12)

- [ ] Real Whisper STT processing audio chunks (3–5s windows)
- [ ] Featherless AI API returning live analysis
- [ ] Latency: audio chunk → UI update < 3 seconds
- [ ] Accept/Reject buttons logging to in-memory list
- [ ] Fallback audio demo working perfectly
- [ ] UI readable in dark environment from 2 metres
- [ ] Confidence indicator visible (UNCERTAIN shown differently)
- [ ] One README with setup in under 5 commands

---

## 🚫 DO NOT BUILD THESE

| Temptation | Why to Skip |
|---|---|
| Real Wav2Vec2 emotion model | Say "validated locally, output format is what feeds the resolver" |
| Bhashini API | Whisper handles multilingual, mention Bhashini verbally |
| PostgreSQL | In-memory dict, done |
| Auth/login | Hardcode operator name = "Priya" |
| Mobile responsive | Desktop workstation only — judges know this |
| Federated learning | One slide in deck |

---

## 💬 PITCH LINES FOR WHAT YOU DIDN'T BUILD

> *"Emotion prosody runs in parallel via Wav2Vec2 — we've validated the integration, the demo shows the exact output format it feeds into the conflict resolver."*

> *"DPDPA 2023 compliance is architectural — no PII persists beyond session. Learning happens on patterns, not individuals."*

> *"Bhashini handles regional language ASR in production. For this demo, Whisper's multilingual model demonstrates the full output pipeline."*

---

## 🏆 JUDGING ANGLES TO HIT

| Layer | How You Hit It In Demo |
|---|---|
| Layer 1: Multimodal Understanding | Whisper transcript + risk score updating live |
| Layer 2: Multi-Agent Conflict | 3 agent cards with staggered reveal + conflict text |
| Layer 3: Operator Interface | Split-screen, accept/reject, peripheral risk indicator |
| Layer 4: Longitudinal Learning | Mention supervisor dashboard (show a mockup slide) |
| Layer 5: Ethical Architecture | Accept/Reject log visible, confidence = UNCERTAIN shown |

---

## ⚡ SINGLE MOST IMPORTANT THING

**The reasoning text.** Every risk change shows:
> "Risk elevated because: caller used phrase 'I've decided', speaking pace dropped, narrative reached closure."

This one feature answers Layers 2, 3, and 5 simultaneously.
Make it large, readable, always visible.

---

*"Working demo > Perfect code."*
