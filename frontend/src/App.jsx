import { startTransition, useDeferredValue, useEffect, useState } from "react";
import { io } from "socket.io-client";

import AgentPanel from "./components/AgentPanel";
import RiskIndicator from "./components/RiskIndicator";
import SuggestionCard from "./components/SuggestionCard";
import TranscriptPanel from "./components/TranscriptPanel";

const SOCKET_URL = "http://localhost:8000";
const formatDuration = (seconds) =>
  new Date(seconds * 1000).toISOString().slice(11, 19);

export default function App() {
  const [elapsed, setElapsed] = useState(0);
  const [analysis, setAnalysis] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [lastAction, setLastAction] = useState(null);
  const [callActive, setCallActive] = useState(false);
  const deferredTranscript = useDeferredValue(transcript);

  const startCall = () => {
    setCallActive(true);
    setTranscript([]);
    setAnalysis(null);
    setElapsed(0);
    console.log("📞 Call started");
  };

  const endCall = () => {
    setCallActive(false);
    console.log("📞 Call ended");
  };

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      if (callActive) {
        setElapsed((value) => value + 1);
      }
    }, 1000);
    return () => window.clearInterval(intervalId);
  }, [callActive]);

  useEffect(() => {
    if (!callActive) return;

    const socket = io(SOCKET_URL, { transports: ["websocket", "polling"] });
    socket.on("connect", () => {
      console.log("✓ Connected to backend");
      setTranscript([]);
    });
    socket.on("analysis_update", (data) => {
      console.log("📊 Analysis update:", data);
      startTransition(() => setAnalysis(data));
    });
    socket.on("transcript_update", (line) => {
      console.log("📝 Transcript update:", line);
      startTransition(() => setTranscript((current) => [...current, line]));
    });
    socket.on("connect_error", (error) => {
      console.error("❌ Connection error:", error);
    });
    socket.on("disconnect", () => console.log("⚠️ Disconnected from backend"));
    return () => socket.close();
  }, [callActive]);

  const logAction = (action) => {
    const entry = { action, timestamp: new Date().toISOString() };
    setLastAction(entry);
    console.log(entry);
  };

  return (
    <div className="app-shell font-mono">
      <header className="header-bar text-[var(--color-text-secondary)]">
        {!callActive ? (
          <button
            onClick={startCall}
            className="px-4 py-2 bg-[var(--risk-high-bg)] border border-[var(--risk-high-border)] text-[var(--risk-high-text)] rounded text-sm uppercase font-bold hover:bg-[var(--risk-high-border)] hover:text-black transition-all"
          >
            📞 Start ResQ VoiceForward Call
          </button>
        ) : (
          <button
            onClick={endCall}
            className="px-4 py-2 bg-[var(--risk-high-bg)] border border-[var(--risk-high-border)] text-[var(--risk-high-text)] rounded text-sm uppercase font-bold hover:bg-[var(--risk-high-border)] hover:text-black transition-all"
          >
            ⏹ End Call
          </button>
        )}
        <span className="flex items-center gap-2 text-[11px] uppercase tracking-[var(--letter-spacing-caps)]">
          <span className={`live-dot ${callActive ? "text-[var(--risk-high-text)]" : "text-[var(--color-text-secondary)]"}`}>●</span>
          <span>{callActive ? "LIVE" : "IDLE"}</span>
        </span>
        <span className="font-bold text-[var(--color-text-primary)]">VoiceForward</span>
        <span>|</span>
        <span className="text-[13px] uppercase">Operator: Priya</span>
        <span>|</span>
        <span className="text-[var(--color-text-primary)]">{formatDuration(elapsed)}</span>
      </header>
      <main className="left-panel">
        {!callActive ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-4xl mb-4">📞</div>
              <div className="text-[var(--color-text-secondary)] text-lg">
                Click "Start ResQ VoiceForward Call" to begin
              </div>
            </div>
          </div>
        ) : (
          <TranscriptPanel transcript={deferredTranscript} />
        )}
      </main>
      <aside className="right-panel">
        {callActive && analysis && (
          <>
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
          </>
        )}
        {callActive && !analysis && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-[var(--color-text-secondary)]">
              <div className="text-2xl mb-2">⏳</div>
              <div>Waiting for AI analysis...</div>
              <div className="text-xs mt-2">Listening to call audio</div>
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}
