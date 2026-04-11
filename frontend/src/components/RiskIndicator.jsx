import { motion } from "framer-motion";

const riskConfig = {
  LOW: { bg: "var(--risk-low-bg)", border: "var(--risk-low-border)", text: "var(--risk-low-text)", glow: "var(--risk-low-glow)" },
  MEDIUM: { bg: "var(--risk-medium-bg)", border: "var(--risk-medium-border)", text: "var(--risk-medium-text)", glow: "var(--risk-medium-glow)" },
  HIGH: { bg: "var(--risk-high-bg)", border: "var(--risk-high-border)", text: "var(--risk-high-text)", glow: "var(--risk-high-glow)" },
  CRITICAL: { bg: "var(--risk-critical-bg)", border: "var(--risk-critical-border)", text: "var(--risk-critical-text)", glow: "var(--risk-critical-glow)" },
};

export default function RiskIndicator({ riskLevel, riskScore, triggeredSignals }) {
  const current = riskConfig[riskLevel] ?? riskConfig.HIGH;

  return (
    <motion.section
      className="panel-card"
      animate={{
        backgroundColor: current.bg,
        borderColor: current.border,
        boxShadow: `0 0 24px ${current.glow}`,
      }}
      transition={{ duration: 0.6, ease: "easeInOut" }}
    >
      <p className="section-label">AI Risk Analysis</p>
      <div className="mt-3" style={{ color: current.text, fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)" }}>
        {riskScore}
      </div>
      <div className="mt-1 uppercase" style={{ color: current.text, fontSize: "var(--font-size-xl)", letterSpacing: "var(--letter-spacing-caps)" }}>
        {riskLevel}
      </div>
      <ul className="mt-4 space-y-2 text-[13px] text-[var(--color-text-primary)]">
        {triggeredSignals.map((signal) => (
          <li key={signal} className="flex items-start gap-2">
            <span className="text-[var(--risk-high-text)]">●</span>
            <span>{signal}</span>
          </li>
        ))}
      </ul>
    </motion.section>
  );
}
