import { motion } from "framer-motion";

const riskConfig = {
  LOW: { bg: "var(--risk-low-bg)", border: "var(--risk-low-border)", text: "var(--risk-low-text)", glow: "var(--risk-low-glow)" },
  MEDIUM: { bg: "var(--risk-medium-bg)", border: "var(--risk-medium-border)", text: "var(--risk-medium-text)", glow: "var(--risk-medium-glow)" },
  HIGH: { bg: "var(--risk-high-bg)", border: "var(--risk-high-border)", text: "var(--risk-high-text)", glow: "var(--risk-high-glow)" },
  CRITICAL: { bg: "var(--risk-critical-bg)", border: "var(--risk-critical-border)", text: "var(--risk-critical-text)", glow: "var(--risk-critical-glow)" },
};

const confidenceColor = {
  HIGH: "var(--verdict-low)",
  MEDIUM: "var(--verdict-medium)",
  LOW: "var(--verdict-high)",
  UNCERTAIN: "var(--verdict-uncertain)",
};

export default function RiskIndicator({ riskLevel, riskScore, triggeredSignals, confidence, escalated }) {
  const current = riskConfig[riskLevel] ?? riskConfig.HIGH;

  return (
    <motion.section
      className={`panel-card${escalated ? " risk-escalation-pulse" : ""}`}
      animate={{
        backgroundColor: current.bg,
        borderColor: current.border,
        boxShadow: escalated
          ? `0 0 48px ${current.glow}, 0 0 8px ${current.glow}`
          : `0 0 24px ${current.glow}`,
      }}
      transition={{ duration: 0.6, ease: "easeInOut" }}
    >
      <div className="flex items-center justify-between">
        <p className="section-label">AI Risk Analysis</p>
        {confidence && (
          <span
            className="agent-badge"
            style={{ "--badge-color": confidenceColor[confidence] ?? confidenceColor.UNCERTAIN }}
          >
            {confidence === "UNCERTAIN" ? "⚠ UNCERTAIN" : `${confidence} CONF`}
          </span>
        )}
      </div>

      <div
        className="mt-3"
        style={{ color: current.text, fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", lineHeight: 1 }}
      >
        {riskScore}
      </div>
      <div
        className="mt-1 uppercase"
        style={{ color: current.text, fontSize: "var(--font-size-xl)", letterSpacing: "var(--letter-spacing-caps)" }}
      >
        {riskLevel}
      </div>

      <ul className="mt-4 space-y-2 text-[13px] text-[var(--color-text-primary)]">
        {triggeredSignals?.map((signal) => (
          <li key={signal} className="flex items-start gap-2">
            <span style={{ color: current.text }}>●</span>
            <span>{signal}</span>
          </li>
        ))}
      </ul>
    </motion.section>
  );
}
