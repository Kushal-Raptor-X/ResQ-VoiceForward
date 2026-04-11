import { startTransition, useEffect, useState } from "react";
import { io } from "socket.io-client";

import CallHistoryView from "./components/CallHistoryView";
import DashboardView from "./components/DashboardView";
import LiveCall_View from "./components/LiveCall_View";
import NavBar from "./components/NavBar";
import SettingsView from "./components/SettingsView";
import { MOCK_ANALYSIS, MOCK_TRANSCRIPT } from "./mockData";

const SOCKET_URL = "http://localhost:8000";
const formatDuration = (seconds) =>
  new Date(seconds * 1000).toISOString().slice(11, 19);

export default function App() {
  const [activeTab, setActiveTab] = useState("Live Call");
  const [elapsed, setElapsed] = useState(0);
  const [analysis, setAnalysis] = useState(MOCK_ANALYSIS);
  const [transcript, setTranscript] = useState([]);
  const [lastAction, setLastAction] = useState(null);

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
      <NavBar activeTab={activeTab} onTabChange={setActiveTab} />
      {activeTab === "Live Call" ? (
        <LiveCall_View
          transcript={transcript}
          analysis={analysis}
          lastAction={lastAction}
          onAccept={() => logAction("ACCEPT")}
          onModify={() => logAction("MODIFY")}
          onReject={() => logAction("REJECT")}
        />
      ) : activeTab === "Call History" ? (
        <CallHistoryView />
      ) : activeTab === "Settings" ? (
        <SettingsView />
      ) : (
        <DashboardView analysis={analysis} onViewCallHistory={() => setActiveTab("Call History")} />
      )}
    </div>
  );
}
