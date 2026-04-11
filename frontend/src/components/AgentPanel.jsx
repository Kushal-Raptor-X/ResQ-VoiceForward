import { motion } from "framer-motion";

const agents = [
  { key: "language_agent", icon: "🗣", label: "LANGUAGE AGENT", delay: 0 },
  { key: "emotion_agent", icon: "🎭", label: "EMOTION AGENT", delay: 0.2 },
  { key: "narrative_agent", icon: "📖", label: "NARRATIVE AGENT", delay: 0.4 },
];

const verdictColors = {
  LOW: "#22c55e",
  MEDIUM: "#f59e0b", 
  HIGH: "#ef4444",
  CRITICAL: "#ff0000",
  UNCERTAIN: "#a78bfa",
};

const parseBreakdown = (value = "UNCERTAIN - Awaiting analysis.") => {
  const [verdict, ...reasoning] = value.split(" - ");
  return { verdict: verdict.toUpperCase(), reasoning: reasoning.join(" - ") || value };
};

export default function AgentPanel({ agentBreakdown, conflict }) {
  return (
    <div className="space-y-4">
      {agents.map((agent) => {
        const breakdown = parseBreakdown(agentBreakdown?.[agent.key]);
        return (
          <motion.div
            key={agent.key}
            className="rounded-lg border border-[#2a2a2a] bg-[#111111] p-4"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: agent.delay, ease: "easeOut" }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-xl">{agent.icon}</span>
                <span className="text-sm font-bold text-white">{agent.label}</span>
              </div>
              <div className="flex items-center gap-2">
                <span 
                  className="text-sm font-bold uppercase"
                  style={{ color: verdictColors[breakdown.verdict] ?? verdictColors.UNCERTAIN }}
                >
                  {breakdown.verdict}
                </span>
                <span className="text-[#888888]">▼</span>
              </div>
            </div>
            <p className="mt-2 text-sm text-[#b0b0b0]">{breakdown.reasoning}</p>
          </motion.div>
        );
      })}
      
      <motion.div
        className="rounded-lg border border-[#2a2a2a] bg-[#111111] p-4"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2, delay: 0.7, ease: "easeOut" }}
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">⚖️</span>
          <span className="text-sm font-bold text-white">CONFLICT RESOLUTION</span>
        </div>
        <p className="mt-2 text-sm text-[#b0b0b0]">{conflict}</p>
      </motion.div>
    </div>
  );
}
