import { motion } from "framer-motion";

const riskConfig = {
  LOW: { bg: "#0d1f0d", border: "#22c55e", text: "#22c55e", glow: "rgba(34, 197, 94, 0.15)" },
  MEDIUM: { bg: "#1f1a0d", border: "#f59e0b", text: "#f59e0b", glow: "rgba(245, 158, 11, 0.15)" },
  HIGH: { bg: "#1f0d0d", border: "#ef4444", text: "#ef4444", glow: "rgba(239, 68, 68, 0.2)" },
  CRITICAL: { bg: "#2d0505", border: "#ff0000", text: "#ff0000", glow: "rgba(255, 0, 0, 0.3)" },
};

export default function RiskIndicator({ riskLevel, riskScore, triggeredSignals }) {
  const current = riskConfig[riskLevel] ?? riskConfig.HIGH;

  return (
    <motion.div
      className="rounded-lg border p-6"
      animate={{
        backgroundColor: current.bg,
        borderColor: current.border,
        boxShadow: `0 0 24px ${current.glow}`,
      }}
      transition={{ duration: 0.6, ease: "easeInOut" }}
    >
      <div className="flex items-center justify-between">
        <div className="text-6xl font-bold" style={{ color: current.text }}>
          {riskScore}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold uppercase tracking-wider" style={{ color: current.text }}>
            {riskLevel}
          </div>
          <div className="mt-1 text-sm text-[#888888]">
            CONFIDENCE: <span className="font-bold text-white">HIGH</span>
          </div>
        </div>
      </div>
      
      <div className="mt-6 space-y-2">
        {triggeredSignals.map((signal, index) => (
          <div key={index} className="flex items-start gap-2 text-sm text-[#e5e5e5]">
            <span className="text-[#ef4444]">▸</span>
            <span>{signal}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
