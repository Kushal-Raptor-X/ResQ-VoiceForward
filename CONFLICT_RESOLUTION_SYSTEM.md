# Multi-Agent Conflict Resolution & Explainable Decision Engine

## Overview

A transparent, safety-first AI decision system for real-time crisis call analysis that resolves conflicts between multiple specialized agents with full explainability.

---

## System Architecture

### 1. Backend: Conflict Resolution Engine (`backend/conflict_resolver.py`)

**Purpose**: Resolves disagreements between AI agents analyzing different dimensions of crisis calls.

**Key Features**:
- ✅ Weighted scoring based on agent confidence
- ✅ Safety-first conflict resolution rules
- ✅ Calibrated uncertainty detection
- ✅ Plain-language explanations
- ✅ Full transparency and auditability

**Input Format**:
```python
{
    "language_agent": {
        "level": "HIGH",
        "signals": ["I've decided", "final statements"],
        "reasoning": "Finality language detected",
        "confidence": 82
    },
    "emotion_agent": {
        "level": "MEDIUM",
        "signals": ["flat tone"],
        "reasoning": "Low emotional variation",
        "confidence": 65
    },
    "audio_agent": {
        "level": "LOW",
        "signals": ["quiet background"],
        "reasoning": "No distress audio cues",
        "confidence": 70
    },
    "narrative_agent": {
        "level": "HIGH",
        "signals": ["story conclusion pattern"],
        "reasoning": "Narrative reaching endpoint",
        "confidence": 78
    }
}
```

**Output Format**:
```python
{
    "final_risk": "HIGH",
    "confidence_summary": "MODERATE",
    "uncertainty": true,
    "explanation": "I'm flagging HIGH risk because...",
    "contributing_factors": [...],
    "conflicting_signals": [...],
    "agent_votes": {...},
    "weighted_score": 2.73
}
```

---

## Resolution Rules (Safety-First)

### Priority Order:
1. **CRITICAL present** → Always escalate to CRITICAL
2. **Conflict with HIGH** → Default to HIGH
3. **Majority HIGH** → Return HIGH
4. **Mixed MEDIUM/HIGH** → Lean HIGH
5. **All LOW** → Return LOW

### Uncertainty Detection:
- ✅ Strong disagreement (3+ different levels)
- ✅ Wide confidence variance (>30% difference)
- ✅ Low average confidence (<60%)

---

## Frontend Components

### 1. AgentExplanationPanel (`frontend/src/components/AgentExplanationPanel.jsx`)

**Purpose**: Display individual agent assessments with full transparency.

**Features**:
- Shows detected signals (e.g., "I've decided")
- Pattern interpretation (e.g., "Finality language detected")
- Confidence score with visual progress bar
- Color-coded risk levels
- Staggered animations

**Visual Example**:
```
🗣 LANGUAGE AGENT                    HIGH ▲
   → Detected: "I've decided"
   → Pattern: Finality language detected
   → Confidence: ████████████░░░░░░░░ 82%
```

---

### 2. LiveDistressIndicators (`frontend/src/components/LiveDistressIndicators.jsx`)

**Purpose**: Real-time monitoring of caller psychological state.

**Indicators**:
- ⚠️ **Distress Intensity** - Overall emotional distress level
- 🧠 **Cognitive Coherence** - Clarity and logical flow of thought
- ⚡ **Agitation** - Physical/emotional restlessness
- 🌀 **Dissociation Markers** - Detachment from reality indicators
- 🚨 **Suicidal Ideation** - Self-harm or suicide risk indicators
- 😓 **Operator Fatigue** - Operator stress and vicarious trauma

**Features**:
- Dynamic progress bars that update in real-time
- Color-coded levels (green → yellow → amber → red)
- Pulse animations for high-risk indicators
- Critical alert banner for suicidal ideation ≥70%
- Live indicator badge

**Visual Behavior**:
- Bars animate smoothly as values change
- High values (≥60%) show pulsing effect
- Critical values trigger alert banners
- Descriptions appear for elevated indicators

---

### 3. ConflictResolutionPanel (`frontend/src/components/ConflictResolutionPanel.jsx`)

**Purpose**: Display final decision with full reasoning chain.

**Sections**:
1. **Final Risk Assessment** - Large, color-coded verdict
2. **Agent Votes Breakdown** - How each agent voted
3. **Contributing Factors** - Key reasons for the decision
4. **Conflicting Signals** - Highlighted disagreements
5. **Detailed Explanation** - Full plain-language reasoning

**Features**:
- Glowing borders for risk levels
- Uncertainty warnings
- Weighted risk score display
- Staggered card animations

---

## Design Principles

### 1. Transparency
- ✅ Never output black-box results
- ✅ Always explain WHY
- ✅ Show all agent votes
- ✅ Highlight conflicts explicitly

### 2. Safety-First
- ✅ Always default to higher risk when unsure
- ✅ Escalate on conflict
- ✅ Conservative policy enforcement

### 3. Calibrated Uncertainty
- ✅ Never appear overly certain
- ✅ Flag conflicting signals
- ✅ Show confidence variance
- ✅ Explicit uncertainty indicators

### 4. Readability
- ✅ Plain language explanations
- ✅ Scannable bullet points
- ✅ Visual hierarchy
- ✅ Color coding for quick assessment
- ✅ Readable in <2 seconds

---

## Integration Guide

### Backend Integration

```python
from conflict_resolver import ConflictResolver

resolver = ConflictResolver()

# Get agent outputs from your AI models
agent_outputs = {
    "language_agent": {...},
    "emotion_agent": {...},
    "audio_agent": {...},
    "narrative_agent": {...}
}

# Resolve conflicts
result = resolver.resolve(agent_outputs)

# Send to frontend via Socket.IO
socketio.emit('conflict_resolution_update', {
    'final_risk': result.final_risk,
    'confidence_summary': result.confidence_summary,
    'uncertainty': result.uncertainty,
    'explanation': result.explanation,
    'contributing_factors': result.contributing_factors,
    'conflicting_signals': result.conflicting_signals,
    'agent_votes': result.agent_votes,
    'weighted_score': result.weighted_score
})
```

### Frontend Integration

```jsx
import ConflictResolutionPanel from './components/ConflictResolutionPanel';
import LiveDistressIndicators from './components/LiveDistressIndicators';
import AgentExplanationPanel from './components/AgentExplanationPanel';

function Dashboard() {
  const [conflictResolution, setConflictResolution] = useState(null);
  const [distressIndicators, setDistressIndicators] = useState({});
  const [agentExplanation, setAgentExplanation] = useState({});

  useEffect(() => {
    socket.on('conflict_resolution_update', setConflictResolution);
    socket.on('distress_indicators_update', setDistressIndicators);
    socket.on('agent_explanation_update', setAgentExplanation);
  }, []);

  return (
    <>
      <LiveDistressIndicators 
        indicators={distressIndicators}
        isLive={true}
      />
      <AgentExplanationPanel 
        agentData={agentExplanation}
        conflict={agentExplanation.conflict}
      />
      <ConflictResolutionPanel 
        resolution={conflictResolution}
      />
    </>
  );
}
```

---

## Testing

Run the test suite:
```bash
cd backend
python test_conflict_resolver.py
```

**Test Scenarios**:
1. HIGH risk with conflicting signals
2. CRITICAL risk scenario
3. LOW risk scenario
4. JSON output format validation

---

## Color Coding

### Risk Levels:
- 🟢 **LOW** - Green (#22c55e)
- 🟡 **MEDIUM** - Amber (#f59e0b)
- 🔴 **HIGH** - Red (#ef4444)
- 🔴🔴 **CRITICAL** - Dark Red (#dc2626)

### Confidence:
- 🟢 **HIGH** - Green
- 🟡 **MODERATE** - Amber
- 🔴 **LOW** - Red
- 🟣 **UNCERTAIN** - Purple (#a78bfa)

---

## Key Metrics

### Weighted Score Calculation:
```
weighted_score = Σ(risk_value × confidence) / Σ(confidence)

Where:
- LOW = 1
- MEDIUM = 2
- HIGH = 3
- CRITICAL = 4
```

### Confidence Summary:
- **HIGH**: avg_confidence ≥ 80% AND no uncertainty
- **MODERATE**: avg_confidence ≥ 60%
- **LOW**: avg_confidence < 60%
- **UNCERTAIN**: Strong disagreement OR wide variance

---

## Live Dynamic Updates

The system updates in real-time as the caller speaks:

1. **Distress Indicators** - Update every 2-3 seconds based on:
   - Tone analysis
   - Word choice
   - Speaking pace
   - Emotional markers

2. **Agent Assessments** - Recalculated continuously:
   - Language patterns
   - Emotional state
   - Narrative progression
   - Audio environment

3. **Conflict Resolution** - Triggered on:
   - New agent outputs
   - Significant indicator changes
   - Risk level transitions

---

## Safety Features

### Critical Alert System:
- 🚨 Automatic alert when suicidal ideation ≥ 70%
- 🔴 Red banner with crisis protocol reminder
- 📢 Visual and (optional) audio notification

### Operator Protection:
- 😓 Operator fatigue monitoring
- ⚠️ Vicarious trauma indicators
- 🔄 Suggested break recommendations

---

## Future Enhancements

- [ ] Historical trend analysis
- [ ] Predictive risk escalation
- [ ] Multi-language support
- [ ] Voice stress analysis integration
- [ ] Supervisor dashboard
- [ ] Automated escalation triggers

---

## License & Credits

Built for RESQ VOICEFORWARD - AI-Augmented Crisis Response Intelligence System

**Design Principles**: Transparency, Safety-First, Explainability
**Target Users**: Crisis helpline operators
**Environment**: High-stress, time-critical decision support
