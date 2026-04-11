import { startTransition, useDeferredValue, useEffect, useState } from "react";
import { io } from "socket.io-client";

import AgentPanel from "./components/AgentPanel";
import RiskIndicator from "./components/RiskIndicator";
import SuggestionCard from "./components/SuggestionCard";
import TranscriptPanel from "./components/TranscriptPanel";
import { MOCK_ANALYSIS, MOCK_TRANSCRIPT } from "./mockData";

const SOCKET_URL = "http://localhost:8000";
const formatDuration = (seconds) =>
  new Date(seconds * 1000).toISOString().slice(11, 19);

export default function App() {
  const [elapsed, setElapsed] = useState(0);
  const [analysis, setAnalysis] = useState(MOCK_ANALYSIS);
  const [transcript, setTranscript] = useState([]);
  const [lastAction, setLastAction] = useState(null);
  const deferredTranscript = useDeferredValue(transcript);

  useEffect(() => {
    const intervalId = window.setInterval(() => setElapsed((value) => value + 1), 1000);
    return () => window.clearInterval(intervalId);
  }, []);

  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ["websocket", "polling"] });
    socket.on("connect", () => setTranscript([]));
    socket.on("analysis_update", (data) => startTransition(() => setAnalysis(data)));
    socket.on("transcript_update", (line) => {
      startTransition(() => setTranscript((current) => [...current, line]));
    });
    socket.on("connect_error", () => {
      setAnalysis(MOCK_ANALYSIS);
      setTranscript((current) => (current.length ? current : MOCK_TRANSCRIPT));
    });
    return () => socket.close();
  }, []);

  const logAction = (action) => {
    const entry = { action, timestamp: new Date().toISOString() };
    setLastAction(entry);
    console.log(entry);
  };

  return (
    <div className="app-shell font-mono">
      <header className="header-bar text-[var(--color-text-secondary)]">
        <span className="flex items-center gap-2 text-[11px] uppercase tracking-[var(--letter-spacing-caps)]">
          <span className="live-dot text-[var(--risk-high-text)]">●</span>
          <span>Live</span>
        </span>
        <span className="font-bold text-[var(--color-text-primary)]">VoiceForward</span>
        <span>|</span>
        <span className="text-[13px] uppercase">Operator: Priya</span>
        <span>|</span>
        <span className="text-[var(--color-text-primary)]">{formatDuration(elapsed)}</span>
      </header>
      <main className="left-panel">
        <TranscriptPanel transcript={deferredTranscript} />
      </main>
      <aside className="right-panel">
        <RiskIndicator
          riskLevel={analysis.risk_level}
          riskScore={analysis.risk_score}
          triggeredSignals={analysis.triggered_signals}
        />
        <AgentPanel agentBreakdown={analysis.agent_breakdown} conflict={analysis.conflict} />
        <SuggestionCard
          suggestedResponse={analysis.suggested_response}
          operatorNote={analysis.operator_note}
          lastAction={lastAction}
          onAccept={() => logAction("ACCEPT")}
          onModify={() => logAction("MODIFY")}
          onReject={() => logAction("REJECT")}
        />
      </aside>
    </div>
  );
}
