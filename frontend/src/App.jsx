import { startTransition, useCallback, useDeferredValue, useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

import AgentPanel from "./components/AgentPanel";
import AmbientPanel from "./components/AmbientPanel";
import AuditLog from "./components/AuditLog";
import CallHistoryView from "./components/CallHistoryView";
import DashboardView from "./components/DashboardView";
import DisclosureBanner from "./components/DisclosureBanner";
import FailureModeBanner from "./components/FailureModeBanner";
import NavBar from "./components/NavBar";
import ReasoningBar from "./components/ReasoningBar";
import ResourcePanel from "./components/ResourcePanel";
import RiskIndicator from "./components/RiskIndicator";
import SettingsView from "./components/SettingsView";
import SuggestionCard from "./components/SuggestionCard";
import SupervisorDashboard from "./components/SupervisorDashboard";
import TranscriptPanel from "./components/TranscriptPanel";
import { MOCK_ANALYSIS, MOCK_TRANSCRIPT } from "./mockData";

const SOCKET_URL = "http://localhost:8000";
const formatDuration = (s) => new Date(s * 1000).toISOString().slice(11, 19);

// Initial state before call starts - neutral/waiting state
const INITIAL_ANALYSIS = {
  risk_level: "LOW",
  risk_score: 0,
  triggered_signals: ["Waiting for call data..."],
  agent_breakdown: {
    language_agent: "WAITING - No data yet",
    emotion_agent: "WAITING - No data yet",
    narrative_agent: "WAITING - No data yet"
  },
  conflict: "Insufficient data for analysis. Start call to begin monitoring.",
  conflict_resolution: "",
  suggested_response: "Waiting for call to start...",
  operator_note: "Click 'Start Call Transcript' to begin monitoring.",
  confidence: "UNCERTAIN",
  ambient_signals: [],
  resources: []
};

export default function App() {
  const [activeTab, setActiveTab] = useState("Live Call");
  const [elapsed, setElapsed] = useState(0);
  const [analysis, setAnalysis] = useState(INITIAL_ANALYSIS);  // Start with initial state
  const [prevRiskLevel, setPrevRiskLevel] = useState(INITIAL_ANALYSIS.risk_level);
  const [riskEscalated, setRiskEscalated] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [connected, setConnected] = useState(false);
  const [callStarted, setCallStarted] = useState(false);  // Track if call has been started
  const [showSupervisor, setShowSupervisor] = useState(false);
  const [disclosureDismissed, setDisclosureDismissed] = useState(false);
  const [aiEnabled, setAiEnabled] = useState(true);       // Layer 3: opt-out
  const [failureMode, setFailureMode] = useState(null);   // Layer 5: stt_fail | model_misclassify | resource_error
  const socketRef = useRef(null);
  const deferredTranscript = useDeferredValue(transcript);

  const RISK_ORDER = { LOW: 0, MEDIUM: 1, HIGH: 2, CRITICAL: 3 };

  // Call timer - only runs when call is started
  useEffect(() => {
    if (!callStarted) return;
    const id = window.setInterval(() => setElapsed((v) => v + 1), 1000);
    return () => window.clearInterval(id);
  }, [callStarted]);

  // Socket connection
  useEffect(() => {
    if (!callStarted) return; // Only connect when call is started
    
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
  }, [callStarted]);

  const handleStopCall = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
    }
    setCallStarted(false);
    setConnected(false);
    setElapsed(0);
    setTranscript([]);
    setAnalysis(INITIAL_ANALYSIS);
    setAuditLog([]);
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
      // Only handle shortcuts when on Live Call tab and not typing in an input
      if (activeTab !== "Live Call" || e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      
      if (e.key === "a" || e.key === "A") { e.preventDefault(); logAction("ACCEPT"); }
      if (e.key === "m" || e.key === "M") { e.preventDefault(); logAction("MODIFY"); }
      if (e.key === "r" || e.key === "R") { e.preventDefault(); logAction("REJECT"); }
      if (e.key === "s" || e.key === "S") { e.preventDefault(); setShowSupervisor((v) => !v); }
      if (e.key === "o" || e.key === "O") { e.preventDefault(); setAiEnabled((v) => !v); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [logAction, activeTab]);

  if (showSupervisor) {
    return <SupervisorDashboard auditLog={auditLog} onClose={() => setShowSupervisor(false)} />;
  }

  // Render Live Call view (full main functionality)
  const renderLiveCallView = () => (
    <>
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
    </>
  );

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
        {/* Live indicator - always visible when call is active */}
        {callStarted && (
          <span className="flex items-center gap-2 text-[11px] uppercase tracking-[var(--letter-spacing-caps)]">
            <span className="live-dot" style={{ color: connected ? "var(--risk-high-text)" : "var(--color-text-muted)" }}>●</span>
            <span>{connected ? "Live" : "Demo"}</span>
          </span>
        )}
        
        <span className="font-bold text-[var(--color-text-primary)]">ResQ VoiceForward</span>
        <span>|</span>
        <span className="text-[13px] uppercase">Operator: Priya</span>
        <span>|</span>
        
        {/* Start/Stop button */}
        {!callStarted ? (
          <button
            type="button"
            onClick={() => setCallStarted(true)}
            className="flex items-center gap-2 text-[11px] uppercase tracking-[var(--letter-spacing-caps)] px-3 py-1 rounded border border-[var(--verdict-low)] text-[var(--verdict-low)] hover:bg-[var(--btn-accept-bg)] transition-colors"
          >
            <span>▶</span>
            <span>Start Call</span>
          </button>
        ) : (
          <button
            type="button"
            onClick={handleStopCall}
            className="flex items-center gap-2 text-[11px] uppercase tracking-[var(--letter-spacing-caps)] px-3 py-1 rounded border border-[var(--risk-high-border)] text-[var(--risk-high-text)] hover:bg-[var(--btn-reject-bg)] transition-colors"
          >
            <span>■</span>
            <span>Stop Call</span>
          </button>
        )}
        
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

      {/* NEW: Navigation Tabs */}
      <NavBar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Render content based on active tab */}
      {activeTab === "Live Call" ? (
        renderLiveCallView()
      ) : activeTab === "Dashboard" ? (
        <div className="dashboard-container">
          <DashboardView analysis={analysis} onViewCallHistory={() => setActiveTab("Call History")} />
        </div>
      ) : activeTab === "Call History" ? (
        <div className="dashboard-container">
          <CallHistoryView />
        </div>
      ) : activeTab === "Settings" ? (
        <div className="dashboard-container">
          <SettingsView />
        </div>
      ) : null}
    </div>
  );
}
