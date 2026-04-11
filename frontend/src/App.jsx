import { startTransition, useDeferredValue, useEffect, useState } from "react";
import { io } from "socket.io-client";

import AgentExplanationPanel from "./components/AgentExplanationPanel";
import ConflictResolutionPanel from "./components/ConflictResolutionPanel";
import LiveDistressIndicators from "./components/LiveDistressIndicators";
import RiskIndicator from "./components/RiskIndicator";
import SuggestionCard from "./components/SuggestionCard";
import TranscriptPanel from "./components/TranscriptPanel";
import { 
  MOCK_ANALYSIS, 
  MOCK_AGENT_EXPLANATION, 
  MOCK_CONFLICT_RESOLUTION,
  MOCK_DISTRESS_INDICATORS,
  MOCK_TRANSCRIPT 
} from "./mockData";

const SOCKET_URL = "http://localhost:8000";
const formatDuration = (seconds) =>
  new Date(seconds * 1000).toISOString().slice(11, 19);

export default function App() {
  const [elapsed, setElapsed] = useState(273); // Start at 04:33
  const [analysis, setAnalysis] = useState(MOCK_ANALYSIS);
  const [agentExplanation, setAgentExplanation] = useState(MOCK_AGENT_EXPLANATION);
  const [conflictResolution, setConflictResolution] = useState(MOCK_CONFLICT_RESOLUTION);
  const [distressIndicators, setDistressIndicators] = useState(MOCK_DISTRESS_INDICATORS);
  const [transcript, setTranscript] = useState([]);
  const [lastAction, setLastAction] = useState(null);
  const [isLive, setIsLive] = useState(false);
  const deferredTranscript = useDeferredValue(transcript);

  useEffect(() => {
    const intervalId = window.setInterval(() => setElapsed((value) => value + 1), 1000);
    return () => window.clearInterval(intervalId);
  }, []);

  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ["websocket", "polling"] });
    socket.on("connect", () => {
      setTranscript([]);
      setIsLive(true);
    });
    socket.on("analysis_update", (data) => startTransition(() => setAnalysis(data)));
    socket.on("agent_explanation_update", (data) => startTransition(() => setAgentExplanation(data)));
    socket.on("conflict_resolution_update", (data) => startTransition(() => setConflictResolution(data)));
    socket.on("distress_indicators_update", (data) => startTransition(() => setDistressIndicators(data)));
    socket.on("transcript_update", (line) => {
      startTransition(() => setTranscript((current) => [...current, line]));
    });
    socket.on("connect_error", () => {
      setAnalysis(MOCK_ANALYSIS);
      setAgentExplanation(MOCK_AGENT_EXPLANATION);
      setConflictResolution(MOCK_CONFLICT_RESOLUTION);
      setDistressIndicators(MOCK_DISTRESS_INDICATORS);
      setTranscript((current) => (current.length ? current : MOCK_TRANSCRIPT));
      setIsLive(false);
    });
    socket.on("disconnect", () => setIsLive(false));
    return () => socket.close();
  }, []);

  const logAction = (action) => {
    const entry = { action, timestamp: new Date().toISOString() };
    setLastAction(entry);
    console.log(entry);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] font-sans">
      {/* Top Navigation */}
      <nav className="border-b border-[#2a2a2a] bg-[#111111] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold text-white">RESQ VOICEFORWARD</h1>
            <div className="flex items-center gap-6 text-sm text-[#888888]">
              <a href="#" className="hover:text-white">DASHBOARD</a>
              <span className="text-white">LIVE CALL</span>
              <a href="#" className="hover:text-white">CALL HISTORY</a>
              <a href="#" className="hover:text-white">ANALYTICS</a>
              <a href="#" className="hover:text-white">SETTINGS</a>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>
              <span className="text-red-500 font-bold font-mono tracking-widest text-lg">LIVE</span>
            </span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Left Panel - Transcript */}
        <div className="w-[60%] border-r border-[#2a2a2a] bg-[#0a0a0a] flex flex-col">
          <div className="border-b border-[#2a2a2a] bg-[#111111] px-6 py-3 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 text-sm text-[#888888]">
                <span>Operator: <span className="text-white">Priya</span></span>
                <span>Call Duration: <span className="font-mono text-white">{formatDuration(elapsed)}</span></span>
                <span className="rounded bg-green-600 px-2 py-1 text-xs font-medium text-white">CALL ACTIVE</span>
              </div>
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <TranscriptPanel transcript={deferredTranscript} />
          </div>
        </div>

        {/* Right Panel - Analysis */}
        <div className="w-[40%] bg-[#0a0a0a] flex flex-col overflow-hidden">
          {/* Suggested Response - Fixed at top for quick access */}
          <div className="flex-shrink-0 border-b border-[#2a2a2a] bg-[#0a0a0a]">
            <div className="p-4">
              <SuggestionCard
                suggestedResponse={analysis.suggested_response}
                operatorNote={analysis.operator_note}
                lastAction={lastAction}
                onAccept={() => logAction("ACCEPT")}
                onModify={() => logAction("MODIFY")}
                onReject={() => logAction("REJECT")}
              />
            </div>
          </div>
          
          {/* Scrollable Analysis Section */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              <RiskIndicator
                riskLevel={analysis.risk_level}
                riskScore={analysis.risk_score}
                triggeredSignals={analysis.triggered_signals}
              />
              
              <LiveDistressIndicators 
                indicators={distressIndicators}
                isLive={isLive}
              />
              
              <AgentExplanationPanel 
                agentData={agentExplanation}
                conflict={agentExplanation.conflict}
              />
              
              <ConflictResolutionPanel 
                resolution={conflictResolution}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
