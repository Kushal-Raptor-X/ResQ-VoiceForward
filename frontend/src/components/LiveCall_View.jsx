import { useDeferredValue } from "react";

import AgentPanel from "./AgentPanel";
import RiskIndicator from "./RiskIndicator";
import SuggestionCard from "./SuggestionCard";
import TranscriptPanel from "./TranscriptPanel";

export default function LiveCall_View({ transcript, analysis, lastAction, onAccept, onModify, onReject }) {
  const deferredTranscript = useDeferredValue(transcript);

  return (
    <>
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
          onAccept={onAccept}
          onModify={onModify}
          onReject={onReject}
        />
      </aside>
    </>
  );
}
