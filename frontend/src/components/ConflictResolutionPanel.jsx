import { motion } from "framer-motion";

const verdictConfig = {
  CRITICAL: { color: "#dc2626", bg: "#450a0a", symbol: "▲▲" },
  HIGH: { color: "#ef4444", bg: "#450a0a", symbol: "▲" },
  MEDIUM: { color: "#f59e0b", bg: "#451a03", symbol: "●" },
  LOW: { color: "#22c55e", bg: "#14532d", symbol: "▼" },
};

const confidenceConfig = {
  HIGH: { color: "#22c55e", text: "HIGH CONFIDENCE" },
  MODERATE: { color: "#f59e0b", text: "MODERATE CONFIDENCE" },
  LOW: { color: "#ef4444", text: "LOW CONFIDENCE" },
  UNCERTAIN: { color: "#a78bfa", text: "UNCERTAIN" },
};

export default function ConflictResolutionPanel({ resolution }) {
  if (!resolution) return null;

  const verdict = verdictConfig[resolution.final_risk] || verdictConfig.MEDIUM;
  const confidence = confidenceConfig[resolution.confidence_summary] || confidenceConfig.MODERATE;

  return (
    <div className="space-y-4">
      {/* Final Decision Card */}
      <motion.div
        className="rounded-lg border-2 p-5"
        style={{ 
          borderColor: verdict.color,
          backgroundColor: verdict.bg,
          boxShadow: `0 0 20px ${verdict.color}30`
        }}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-white tracking-wider">
            FINAL RISK ASSESSMENT
          </h3>
          <div className="flex items-center gap-2">
            <span 
              className="text-2xl font-bold tracking-wider"
              style={{ color: verdict.color }}
            >
              {resolution.final_risk}
            </span>
            <span style={{ color: verdict.color }}>{verdict.symbol}</span>
          </div>
        </div>

        {/* Confidence & Uncertainty */}
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-[#888888]">Confidence:</span>
            <span 
              className="font-bold"
              style={{ color: confidence.color }}
            >
              {confidence.text}
            </span>
          </div>
          {resolution.uncertainty && (
            <div className="flex items-center gap-2">
              <span className="text-[#a78bfa]">⚠️</span>
              <span className="text-[#a78bfa] font-bold">UNCERTAINTY DETECTED</span>
            </div>
          )}
        </div>

        {/* Weighted Score */}
        <div className="mt-3 pt-3 border-t border-[#2a2a2a]">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[#888888]">Weighted Risk Score:</span>
            <span className="font-mono font-bold text-white">
              {resolution.weighted_score?.toFixed(2) || "N/A"} / 4.0
            </span>
          </div>
        </div>
      </motion.div>

      {/* Agent Votes Breakdown */}
      <motion.div
        className="rounded-lg border border-[#2a2a2a] bg-[#111111] p-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <h4 className="text-xs font-bold text-white tracking-wider mb-3">
          AGENT VOTES
        </h4>
        <div className="space-y-2">
          {Object.entries(resolution.agent_votes || {}).map(([agent, level], index) => {
            const agentVerdict = verdictConfig[level] || verdictConfig.MEDIUM;
            return (
              <div key={agent} className="flex items-center justify-between text-xs">
                <span className="text-[#e5e5e5]">{agent}</span>
                <span 
                  className="font-bold"
                  style={{ color: agentVerdict.color }}
                >
                  {level} {agentVerdict.symbol}
                </span>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Contributing Factors */}
      <motion.div
        className="rounded-lg border border-[#2a2a2a] bg-[#111111] p-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <h4 className="text-xs font-bold text-white tracking-wider mb-3">
          KEY CONTRIBUTING FACTORS
        </h4>
        <ul className="space-y-2">
          {resolution.contributing_factors?.map((factor, index) => (
            <li key={index} className="flex items-start gap-2 text-xs text-[#e5e5e5]">
              <span className="text-[#ef4444] mt-0.5">▸</span>
              <span>{factor}</span>
            </li>
          ))}
        </ul>
      </motion.div>

      {/* Conflicting Signals (if any) */}
      {resolution.conflicting_signals && resolution.conflicting_signals.length > 0 && (
        <motion.div
          className="rounded-lg border-2 border-[#a78bfa] bg-[#1a1625] p-4"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <div className="flex items-center gap-2 mb-3">
            <span className="text-base">⚠️</span>
            <h4 className="text-xs font-bold text-[#a78bfa] tracking-wider">
              CONFLICTING SIGNALS DETECTED
            </h4>
          </div>
          <ul className="space-y-2">
            {resolution.conflicting_signals.map((signal, index) => (
              <li key={index} className="flex items-start gap-2 text-xs text-[#c4b5fd]">
                <span className="mt-0.5">•</span>
                <span>{signal}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Full Explanation */}
      <motion.div
        className="rounded-lg border border-[#2a2a2a] bg-[#111111] p-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.4 }}
      >
        <h4 className="text-xs font-bold text-white tracking-wider mb-3">
          DETAILED EXPLANATION
        </h4>
        <div className="text-xs text-[#e5e5e5] leading-relaxed whitespace-pre-line font-sans">
          {resolution.explanation}
        </div>
      </motion.div>
    </div>
  );
}
