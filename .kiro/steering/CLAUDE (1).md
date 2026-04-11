# CLAUDE.md — VoiceForward UI Design System Rules
### For use by Codex, Kiro, Copilot, and any AI coding assistant

---

## 1. PROJECT IDENTITY

- **App name:** VoiceForward
- **Context:** Crisis helpline operator workstation dashboard
- **Environment:** Desktop only (1440px+ minimum), dark room, high-stress use
- **Aesthetic:** Industrial-utilitarian. Think mission control, not SaaS. Every pixel earns its place.
- **Golden rule:** The UI must be readable from 2 metres away. Risk level must be visible at a glance.

---

## 2. COLOR TOKENS (CSS Variables — define in index.css)

```css
:root {
  /* Base surfaces */
  --color-bg-base:        #0a0a0a;   /* page background */
  --color-bg-panel:       #111111;   /* card/panel background */
  --color-bg-panel-hover: #181818;   /* hovered panel */
  --color-bg-input:       #1a1a1a;   /* input fields */
  --color-border:         #2a2a2a;   /* subtle dividers */
  --color-border-strong:  #3a3a3a;   /* visible borders */

  /* Text */
  --color-text-primary:   #f0f0f0;   /* main readable text */
  --color-text-secondary: #888888;   /* labels, metadata */
  --color-text-muted:     #555555;   /* placeholders, disabled */

  /* Risk states — the most important tokens */
  --risk-low-bg:          #0d1f0d;
  --risk-low-border:      #22c55e;
  --risk-low-text:        #22c55e;
  --risk-low-glow:        rgba(34, 197, 94, 0.15);

  --risk-medium-bg:       #1f1a0d;
  --risk-medium-border:   #f59e0b;
  --risk-medium-text:     #f59e0b;
  --risk-medium-glow:     rgba(245, 158, 11, 0.15);

  --risk-high-bg:         #1f0d0d;
  --risk-high-border:     #ef4444;
  --risk-high-text:       #ef4444;
  --risk-high-glow:       rgba(239, 68, 68, 0.2);

  --risk-critical-bg:     #2d0505;
  --risk-critical-border: #ff0000;
  --risk-critical-text:   #ff0000;
  --risk-critical-glow:   rgba(255, 0, 0, 0.3);

  /* Agent verdict colours */
  --verdict-high:         #ef4444;
  --verdict-medium:       #f59e0b;
  --verdict-low:          #22c55e;
  --verdict-uncertain:    #a78bfa;

  /* Action buttons */
  --btn-accept-bg:        #14532d;
  --btn-accept-text:      #22c55e;
  --btn-accept-border:    #22c55e;

  --btn-modify-bg:        #451a03;
  --btn-modify-text:      #f59e0b;
  --btn-modify-border:    #f59e0b;

  --btn-reject-bg:        #450a0a;
  --btn-reject-text:      #ef4444;
  --btn-reject-border:    #ef4444;

  /* Highlight for risk phrases in transcript */
  --highlight-risk:       rgba(239, 68, 68, 0.25);
  --highlight-risk-text:  #fca5a5;
}
```

---

## 3. TYPOGRAPHY

```css
/* Font stack — use system monospace for transcript, sans for UI */
--font-ui:          'JetBrains Mono', 'IBM Plex Mono', monospace; /* ALL text */
--font-size-xs:     11px;   /* metadata, timestamps */
--font-size-sm:     13px;   /* secondary labels */
--font-size-base:   14px;   /* body text, transcript */
--font-size-md:     16px;   /* panel headers */
--font-size-lg:     20px;   /* agent verdict text */
--font-size-xl:     28px;   /* risk label (HIGH/CRITICAL) */
--font-size-2xl:    48px;   /* risk score number */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-bold:   700;
--line-height-tight: 1.3;
--line-height-base:  1.6;
--letter-spacing-caps: 0.08em; /* for ALL_CAPS labels */
```

**Why monospace?** Crisis call centres use terminal-style interfaces. Monospace makes transcript text scannable and feels domain-accurate. Never use Inter, Roboto, or system-ui.

---

## 4. SPACING SCALE

```css
--space-1:   4px;
--space-2:   8px;
--space-3:   12px;
--space-4:   16px;
--space-5:   20px;
--space-6:   24px;
--space-8:   32px;
--space-10:  40px;
--space-12:  48px;
```

---

## 5. LAYOUT RULES

### App Shell
```
┌──────────────────────────────────────────────────────┐
│  HEADER BAR  (40px)  — operator name | call timer    │
├───────────────────────────┬──────────────────────────┤
│                           │                          │
│   LEFT PANEL (55%)        │   RIGHT PANEL (45%)      │
│   TranscriptPanel         │   RiskIndicator          │
│                           │   AgentPanel             │
│                           │   SuggestionCard         │
│                           │                          │
└───────────────────────────┴──────────────────────────┘
```

```css
/* App layout */
.app-shell {
  display: grid;
  grid-template-rows: 40px 1fr;
  grid-template-columns: 55fr 45fr;
  height: 100vh;
  width: 100vw;
  background: var(--color-bg-base);
  gap: 0;
}

.header-bar {
  grid-column: 1 / -1;
  background: var(--color-bg-panel);
  border-bottom: 1px solid var(--color-border-strong);
  display: flex;
  align-items: center;
  padding: 0 var(--space-4);
  gap: var(--space-4);
}

.left-panel {
  border-right: 1px solid var(--color-border-strong);
  overflow-y: auto;
  padding: var(--space-4);
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  overflow-y: auto;
}
```

---

## 6. COMPONENT SPECIFICATIONS

### 6.1 TranscriptPanel
- Scrollable list of lines
- Each line: `[timestamp] [CALLER/OPERATOR]: text`
- Risk phrases are wrapped in `<span class="risk-highlight">` — amber background, red text
- New lines appear at the bottom, panel auto-scrolls
- Font: monospace, 14px, line-height 1.6
- Timestamps: muted text, 11px

```jsx
// Risk phrase highlight class
// bg: var(--highlight-risk)
// color: var(--highlight-risk-text)
// border-radius: 2px
// padding: 0 3px
```

### 6.2 RiskIndicator
- Full-width card at top of right panel
- Background, border, text all driven by `risk_level` token
- Box shadow: `0 0 24px var(--risk-{level}-glow)` — glows outward
- Top half: large risk score number (48px, bold, monospace)
- Middle: risk level label in ALL CAPS (28px, letter-spacing 0.08em)
- Bottom: 3 bullet points from `triggered_signals[]` (13px)
- Framer Motion: animate `background`, `borderColor`, `boxShadow` on risk change — duration 0.6s ease

```jsx
const riskConfig = {
  LOW:      { bg: 'var(--risk-low-bg)',      border: 'var(--risk-low-border)',      text: 'var(--risk-low-text)',      glow: 'var(--risk-low-glow)' },
  MEDIUM:   { bg: 'var(--risk-medium-bg)',   border: 'var(--risk-medium-border)',   text: 'var(--risk-medium-text)',   glow: 'var(--risk-medium-glow)' },
  HIGH:     { bg: 'var(--risk-high-bg)',     border: 'var(--risk-high-border)',     text: 'var(--risk-high-text)',     glow: 'var(--risk-high-glow)' },
  CRITICAL: { bg: 'var(--risk-critical-bg)', border: 'var(--risk-critical-border)', text: 'var(--risk-critical-text)', glow: 'var(--risk-critical-glow)' },
}
```

### 6.3 AgentPanel
- Three cards stacked vertically
- Each card: dark panel bg, 1px border, 8px border-radius
- Card structure:
  ```
  [Icon]  LANGUAGE AGENT        [HIGH ▲]
  "Passive farewell language detected"
  ```
- Icon: simple emoji or lucide icon (🗣 🎭 📖)
- Verdict badge: pill shape, color from `--verdict-{level}`
- Stagger animation with framer-motion: delays 0ms / 200ms / 400ms
- After all 3: Conflict Resolution card at 700ms — purple accent (`--verdict-uncertain`)

### 6.4 SuggestionCard
- Appears after agent cards
- Suggested response text in a quote-style box (left border accent, italic)
- Operator note in smaller muted text below
- Three action buttons side by side:
  - ✓ Accept — green
  - ✎ Modify — amber
  - ✗ Reject — red
- Buttons: monospace font, uppercase, 12px, 1px border, no fill by default, fill on hover

### 6.5 Header Bar
```
[● LIVE]  VoiceForward  |  Operator: Priya  |  Call Duration: 00:04:32  |  [CALL ACTIVE badge]
```
- `● LIVE` indicator: red dot, pulsing animation (CSS keyframes)
- Call duration: monospace, ticking every second (setInterval)
- All uppercase labels, muted color, small font

---

## 7. ANIMATION RULES

```js
// Framer Motion — standard transitions
const fastTransition  = { duration: 0.2, ease: 'easeOut' }
const riskTransition  = { duration: 0.6, ease: 'easeInOut' }
const staggerDelay    = (index) => index * 0.2  // for agent cards

// CSS keyframes for pulsing live indicator
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
.live-dot { animation: pulse 1.5s ease-in-out infinite; }
```

---

## 8. TAILWIND CONFIG EXTENSION

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'risk-low':      '#22c55e',
        'risk-medium':   '#f59e0b',
        'risk-high':     '#ef4444',
        'risk-critical': '#ff0000',
        'surface':       '#111111',
        'base':          '#0a0a0a',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"IBM Plex Mono"', 'monospace'],
      },
      boxShadow: {
        'risk-low':      '0 0 24px rgba(34, 197, 94, 0.15)',
        'risk-high':     '0 0 24px rgba(239, 68, 68, 0.2)',
        'risk-critical': '0 0 32px rgba(255, 0, 0, 0.3)',
      }
    }
  }
}
```

---

## 9. DO NOT

- ❌ No white or light backgrounds anywhere
- ❌ No rounded corners > 8px
- ❌ No gradients (except subtle 0.05 opacity overlays)
- ❌ No Inter, Roboto, system-ui fonts
- ❌ No modals or popups — everything inline
- ❌ No hover tooltips — text must be readable without interaction
- ❌ No mobile breakpoints
- ❌ No shadows with colour other than the risk glow tokens
- ❌ No external component libraries (no MUI, Chakra, shadcn)

---

## 10. COMPONENT FILE → CSS TOKEN MAP

| Component | Key tokens used |
|---|---|
| `TranscriptPanel` | `--color-bg-panel`, `--font-size-base`, `--highlight-risk` |
| `RiskIndicator` | `--risk-{level}-*` all four, `--font-size-2xl`, `--font-size-xl` |
| `AgentPanel` | `--verdict-*`, `--color-bg-panel`, `--color-border` |
| `SuggestionCard` | `--btn-accept-*`, `--btn-modify-*`, `--btn-reject-*` |
| `HeaderBar` | `--color-bg-panel`, `--color-text-secondary`, `--color-border-strong` |

---

## 11. MOCK DATA SHAPE (for Codex to use as default state)

```js
export const MOCK_ANALYSIS = {
  risk_level: "HIGH",
  risk_score: 78,
  triggered_signals: [
    "caller used phrase 'I've decided'",
    "speaking pace dropped significantly",
    "unusual calm tone detected"
  ],
  agent_breakdown: {
    language_agent: "HIGH - passive farewell language detected",
    emotion_agent: "MEDIUM - flat affect, minimal emotional variation",
    narrative_agent: "HIGH - story reached a conclusion point"
  },
  conflict: "Language and narrative agents flag HIGH. Emotion agent flags MEDIUM. Defaulting to HIGH per conservative protocol.",
  suggested_response: "It sounds like you've been carrying this for a long time. Can you tell me what today felt like?",
  operator_note: "Do not rush. Caller appears to have made a decision. Keep them talking.",
  confidence: "HIGH"
}

export const MOCK_TRANSCRIPT = [
  { time: "00:01:12", speaker: "CALLER", text: "I've been feeling really low lately.", isRisk: false },
  { time: "00:02:34", speaker: "OPERATOR", text: "Can you tell me more about that?", isRisk: false },
  { time: "00:03:45", speaker: "CALLER", text: "I've been thinking about this for weeks now.", isRisk: true },
  { time: "00:04:20", speaker: "CALLER", text: "I think I've finally decided what I need to do.", isRisk: true },
]
```
