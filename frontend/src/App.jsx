import { startTransition, useCallback, useDeferredValue, useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

import AgentPanel from "./components/AgentPanel";
import AmbientPanel from "./components/AmbientPanel";
import AuditLog from "./components/AuditLog";
import DisclosureBanner from "./components/DisclosureBanner";
import FailureModeBanner from "./components/FailureModeBanner";
import ReasoningBar from "./components/ReasoningBar";
import ResourcePanel from "./components/ResourcePanel";
import RiskIndicator from "./components/RiskIndicator";
import SuggestionCard from "./components/SuggestionCard";
import SupervisorDashboard from "./components/SupervisorDashboard";
import TranscriptPanel from "./components/TranscriptPanel";
import { MOCK_ANALYSIS, MOCK_TRANSCRIPT } from "./mockData";

const SOCKET_URL = "http://localhost:8000";
const formatDuration = (s) => new Date(s * 1000).toISOString().slice(11, 19);

export default function App() {
  const [activeTab, setActiveTab] = useState("Live Call");
  const [elapsed, setElapsed] = useState(0);
  const [analysis, setAnalysis] = useState(MOCK_ANALYSIS);
  const [prevRiskLevel, setPrevRiskLevel] = useState(MOCK_ANALYSIS.risk_level);
  const [riskEscalated, setRiskEscalated] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [connected, setConnected] = useState(false);
  const [showSupervisor, setShowSupervisor] = useState(false);
  const [disclosureDismissed, setDisclosureDismissed] = useState(false);
  const [aiEnabled, setAiEnabled] = useState(true);       // Layer 3: opt-out
  const [failureMode, setFailureMode] = useState(null);   // Layer 5: stt_fail | model_misclassify | resource_error
  const socketRef = useRef(null);
  const deferredTranscript = useDeferredValue(transcript);

  const RISK_ORDER = { LOW: 0, MEDIUM: 1, HIGH: 2, CRITICAL: 3 };

  // Call timer
  useEffect(() => {
    const id = window.setInterval(() => setElapsed((v) => v + 1), 1000);
    return () => window.clearInterval(id);
  }, []);

  // Socket connection
  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ["websocket", "polling"] });
    socketRef.current = socket;

    socket.on("connect", () => { setConnected(true); setTranscript([]); setFailureMode(null); });
    socket.on("disconnect", () => setConnected(false));
    socket.on("analysis_update", (data) => {
      startTransition(() => {
        // Layer 3: detect escalation for flash animation
        setAnalysis((prev) => {
          const prevOrder = RISK_ORDER[prev.risk_level] ?? 0;
          const newOrder = RISK_ORDER[data.risk_level] ?? 0;
          if (newOrder > prevOrder) {
            setRiskEscalated(true);
            setTimeout(() => setRiskEscalated(false), 1500);
          }
          setPrevRiskLevel(prev.risk_level);
          return data;
        });
        // Layer 5: failure mode detection
        if (data.failure_mode) setFailureMode(data.failure_mode);
        else if (data.confidence === "UNCERTAIN" && data.risk_score >= 80) setFailureMode("model_misclassify");
        else setFailureMode(null);
      });
    });
    socket.on("transcript_update", (line) =>
      startTransition(() => setTranscript((cur) => [...cur, line]))
    );
    socket.on("connect_error", () => {
      setConnected(false);
      setFailureMode("stt_fail");
      setAnalysis(MOCK_ANALYSIS);
      setTranscript((cur) => (cur.length ? cur : MOCK_TRANSCRIPT));
    });

    return () => socket.close();
  }, []);

  const logAction = useCallback((action, resourceUsed = null) => {
    const entry = {
      action,
      suggestion: analysis.suggested_response,
      risk_level: analysis.risk_level,
      risk_score: analysis.risk_score,
      confidence: analysis.confidence,
      reasoning: analysis.conflict_resolution || analysis.conflict,
      timestamp: new Date().toISOString(),
      resource_used: resourceUsed,
    };
    setAuditLog((cur) => [entry, ...cur]);
    if (socketRef.current?.connected) {
      socketRef.current.emit("operator_action", entry);
    }
  }, [analysis]);

  // Keyboard shortcuts — Layer 3
  useEffect(() => {
    const handler = (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      if (e.key === "a" || e.key === "A") logAction("ACCEPT");
      if (e.key === "m" || e.key === "M") logAction("MODIFY");
      if (e.key === "r" || e.key === "R") logAction("REJECT");
      if (e.key === "s" || e.key === "S") setShowSupervisor((v) => !v);
      if (e.key === "o" || e.key === "O") setAiEnabled((v) => !v);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [logAction]);

  if (showSupervisor) {
    return <SupervisorDashboard auditLog={auditLog} onClose={() => setShowSupervisor(false)} />;
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Only handle shortcuts when on Live Call tab and not typing in an input
      if (activeTab !== "Live Call" || e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") {
        return;
      }

      switch (e.key.toLowerCase()) {
        case "a":
          e.preventDefault();
          logAction("ACCEPT");
          break;
        case "m":
          e.preventDefault();
          logAction("MODIFY");
          break;
        case "r":
          e.preventDefault();
          logAction("REJECT");
          break;
        case " ":
          e.preventDefault();
          console.log("Toggle call recording");
          break;
        case "escape":
          e.preventDefault();
          console.log("Dismiss alert");
          break;
        case "tab":
          e.preventDefault();
          console.log("Next panel");
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [activeTab]);

  return (
    <div className={`app-shell font-mono${riskEscalated ? " risk-escalation-flash" : ""}`}>
      {/* Layer 5: AI Disclosure Banner */}
      {!disclosureDismissed && (
        <DisclosureBanner onDismiss={() => setDisclosureDismissed(true)} />
      )}

      {/* Layer 5: Failure mode banner */}
      {failureMode && <FailureModeBanner mode={failureMode} onDismiss={() => setFailureMode(null)} />}

      {/* Header */}
      <header className="header-bar text-[var(--color-text-secondary)]">
        <span className="flex items-center gap-2 text-[11px] uppercase tracking-[var(--letter-spacing-caps)]">
          <span className="live-dot" style={{ color: connected ? "var(--risk-high-text)" : "var(--color-text-muted)" }}>●</span>
          <span>{connected ? "Live" : "Demo"}</span>
        </span>
        <span className="font-bold text-[var(--color-text-primary)]">VoiceForward</span>
        <span>|</span>
        <span className="text-[13px] uppercase">Operator: Priya</span>
        <span>|</span>
        <span className="text-[var(--color-text-primary)]">{formatDuration(elapsed)}</span>
        <span>|</span>
        <span
          className="text-[11px] uppercase tracking-[var(--letter-spacing-caps)]"
          style={{
            color: analysis.confidence === "UNCERTAIN"
              ? "var(--verdict-uncertain)"
              : analysis.confidence === "HIGH"
              ? "var(--verdict-low)"
              : "var(--verdict-medium)",
          }}
        >
          {analysis.confidence === "UNCERTAIN" ? "⚠ UNCERTAIN" : `Conf: ${analysis.confidence}`}
        </span>

        {/* Layer 1: Operator fatigue flag */}
        {analysis.operator_fatigue_flag && (
          <span className="text-[11px] uppercase tracking-[var(--letter-spacing-caps)]"
            style={{ color: "var(--verdict-uncertain)" }}>
            ⚠ Operator fatigue detected
          </span>
        )}

        <div className="ml-auto flex items-center gap-3">
          {/* Layer 3: AI opt-out toggle */}
          <button
            type="button"
            onClick={() => setAiEnabled((v) => !v)}
            className="text-[11px] uppercase tracking-[var(--letter-spacing-caps)] px-2 py-1 rounded border transition-colors"
            style={{
              borderColor: aiEnabled ? "var(--verdict-low)" : "var(--color-border)",
              color: aiEnabled ? "var(--verdict-low)" : "var(--color-text-muted)",
            }}
          >
            [O] AI {aiEnabled ? "ON" : "OFF"}
          </button>

          <button
            type="button"
            onClick={() => setShowSupervisor(true)}
            className="text-[11px] uppercase tracking-[var(--letter-spacing-caps)] px-2 py-1 rounded border border-[var(--color-border)] hover:border-[var(--color-border-strong)] text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
          >
            [S] Supervisor
          </button>
        </div>
      </header>

      {/* Layer 2: Reasoning bar — always visible */}
      <ReasoningBar
        riskLevel={analysis.risk_level}
        conflictResolution={analysis.conflict_resolution || analysis.conflict}
        triggeredSignals={analysis.triggered_signals}
        aiEnabled={aiEnabled}
      />

      {/* Left panel — transcript */}
      <main className="left-panel">
        <TranscriptPanel transcript={deferredTranscript} />
      </main>

      {/* Right panel — 3 zones per Layer 3 */}
      <aside className="right-panel">
        {aiEnabled ? (
          <>
            {/* Zone 1: Situational awareness */}
            <RiskIndicator
              riskLevel={analysis.risk_level}
              riskScore={analysis.risk_score}
              triggeredSignals={analysis.triggered_signals}
              confidence={analysis.confidence}
              escalated={riskEscalated}
            />

            {/* Layer 1: Ambient signals */}
            <AmbientPanel signals={analysis.ambient_signals || []} />

            <AgentPanel
              agentBreakdown={analysis.agent_breakdown}
              conflict={analysis.conflict}
              conflictResolution={analysis.conflict_resolution}
            />

            {/* Zone 2: Immediate guidance */}
            <SuggestionCard
              suggestedResponse={analysis.suggested_response}
              operatorNote={analysis.operator_note}
              onAccept={() => logAction("ACCEPT")}
              onModify={() => logAction("MODIFY")}
              onReject={() => logAction("REJECT")}
            />

            {/* Zone 3: Resource readiness */}
            <ResourcePanel
              resources={analysis.resources || []}
              onDispatch={(label) => logAction("ACCEPT", label)}
            />

            {/* Layer 5: Audit log */}
            <AuditLog entries={auditLog} />
          </>
        ) : (
          /* Layer 3: Opt-out — no worse experience, just clean state */
          <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
            <p className="text-[28px]">🔕</p>
            <p className="section-label">AI Assistance Disabled</p>
            <p className="text-[13px] text-[var(--color-text-muted)] max-w-xs">
              Operator is working independently. Transcript continues. Press [O] to re-enable AI assistance.
            </p>
          </div>
        )}
      </aside>
    </div>
  );
}
