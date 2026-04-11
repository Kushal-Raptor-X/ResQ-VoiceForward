import { useCallback, useDeferredValue, useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

import AgentPanel from "./components/AgentPanel";
import RiskIndicator from "./components/RiskIndicator";
import SuggestionCard from "./components/SuggestionCard";
import TranscriptPanel from "./components/TranscriptPanel";
import { MOCK_ANALYSIS, MOCK_TRANSCRIPT } from "./mockData";

const SOCKET_URL = "http://localhost:8000";
const formatDuration = (s) => new Date(s * 1000).toISOString().slice(11, 19);

export default function App() {
  const [elapsed, setElapsed] = useState(0);
  const [analysis, setAnalysis] = useState(MOCK_ANALYSIS);
  const [transcript, setTranscript] = useState(MOCK_TRANSCRIPT);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);
  const deferredTranscript = useDeferredValue(transcript);

  // Call timer
  useEffect(() => {
    const id = window.setInterval(() => setElapsed((v) => v + 1), 1000);
    return () => window.clearInterval(id);
  }, []);

  // Socket connection
  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ["websocket", "polling"] });
    socketRef.current = socket;

    socket.on("connect", () => {
      setConnected(true);
      setTranscript([]);
    });
    socket.on("disconnect", () => setConnected(false));
    socket.on("analysis_update", (data) => {
      setAnalysis(data);
    });
    socket.on("transcript_update", (line) =>
      setTranscript((cur) => [...cur, line])
    );
    socket.on("connect_error", () => {
      setConnected(false);
      setAnalysis(MOCK_ANALYSIS);
      setTranscript(MOCK_TRANSCRIPT);
    });

    return () => socket.close();
  }, []);

  const logAction = useCallback((action) => {
    const entry = {
      action,
      suggestion: analysis.suggested_response,
      risk_level: analysis.risk_level,
      risk_score: analysis.risk_score,
      confidence: analysis.confidence,
      timestamp: new Date().toISOString(),
    };
    if (socketRef.current?.connected) {
      socketRef.current.emit("operator_action", entry);
    }
  }, [analysis]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      if (e.key === "a" || e.key === "A") { e.preventDefault(); logAction("ACCEPT"); }
      if (e.key === "m" || e.key === "M") { e.preventDefault(); logAction("MODIFY"); }
      if (e.key === "r" || e.key === "R") { e.preventDefault(); logAction("REJECT"); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [logAction]);

  return (
    <div className="app-shell font-mono">
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
      </header>

      {/* Left panel — transcript */}
      <main className="left-panel">
        <TranscriptPanel transcript={deferredTranscript} />
      </main>

      {/* Right panel — risk analysis */}
      <aside className="right-panel">
        {/* Zone 1: Situational awareness */}
        <RiskIndicator
          riskLevel={analysis.risk_level}
          riskScore={analysis.risk_score}
          triggeredSignals={analysis.triggered_signals}
          confidence={analysis.confidence}
        />

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
      </aside>
    </div>
  );
}
