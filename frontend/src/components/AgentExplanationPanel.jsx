import { motion } from "framer-motion";

const agents = [
  { key: "language_agent", icon: "🗣", label: "LANGUAGE AGENT", delay: 0 },
  { key: "emotion_agent", icon: "🎭", label: "EMOTION AGENT", delay: 0.15 },
  { key: "narrative_agent", icon: "📖", label: "NARRATIVE AGENT", delay: 0.3 },
];

const verdictConfig = {
  HIGH: { color: "#ef4444", symbol: "▲" },
  MEDIUM: { color: "#f59e0b", symbol: "●" },
  LOW: { color: "#22c55e", symbol: "▼" },
  CRITICAL: { color: "#ff0000", symbol: "▲▲" },
};

export default function AgentExplanationPanel({ agentData, conflict }) {
  return (
    <div className="space-y-3 font-mono">
      {agents.map((agent) => {
        const data = agentData?.[agent.key];
        if (!data) return null;

        const verdict = verdictConfig[data.level] || verdictConfig.MEDIUM;

        return (
          <motion.div
            key={agent.key}
            className="rounded-lg border border-[#2a2a2a] bg-[#111111] p-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: agent.delay, ease: "easeOut" }}
          >
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">{agent.icon}</span>
                <span className="text-xs font-bold tracking-wider text-white">
                  {agent.label}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className="text-xs font-bold tracking-wider"
                  style={{ color: verdict.color }}
                >
                  {data.level}
                </span>
                <span style={{ color: verdict.color }}>{verdict.symbol}</span>
              </div>
            </div>

            {/* Explanation Details */}
            <div className="mt-3 space-y-2 text-xs">
              {/* Detected Signal */}
              <div className="flex items-start gap-2">
                <span className="text-[#888888]">→ Detected:</span>
                <span className="text-[#f59e0b]">"{data.detected}"</span>
              </div>

              {/* Pattern Interpretation */}
              <div className="flex items-start gap-2">
                <span className="text-[#888888]">→ Pattern:</span>
                <span className="text-[#e5e5e5]">{data.pattern}</span>
              </div>

              {/* Confidence Score */}
              <div className="flex items-center gap-2">
                <span className="text-[#888888]">→ Confidence:</span>
                <div className="flex items-center gap-2 flex-1">
                  <div className="h-1.5 flex-1 rounded-full bg-[#1a1a1a] overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ backgroundColor: verdict.color }}
                      initial={{ width: 0 }}
                      animate={{ width: `${data.confidence}%` }}
                      transition={{ duration: 0.8, delay: agent.delay + 0.2 }}
                    />
                  </div>
                  <span className="text-white font-bold w-10 text-right">
                    {data.confidence}%
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        );
      })}

      {/* Conflict Resolution Card */}
      {conflict && (
        <motion.div
          className="rounded-lg border border-[#a78bfa] bg-[#111111] p-4"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.45, ease: "easeOut" }}
        >
          <div className="flex items-center gap-2">
            <span className="text-lg">⚖️</span>
            <span className="text-xs font-bold tracking-wider text-[#a78bfa]">
              CONFLICT RESOLUTION
            </span>
          </div>
          <p className="mt-3 text-xs leading-relaxed text-[#e5e5e5]">
            {conflict}
          </p>
        </motion.div>
      )}
    </div>
  );
}
