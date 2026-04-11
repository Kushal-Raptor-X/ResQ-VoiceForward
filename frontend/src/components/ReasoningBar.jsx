import { AnimatePresence, motion } from "framer-motion";

const riskBorderColor = {
  LOW: "var(--risk-low-border)",
  MEDIUM: "var(--risk-medium-border)",
  HIGH: "var(--risk-high-border)",
  CRITICAL: "var(--risk-critical-border)",
};
const riskTextColor = {
  LOW: "var(--risk-low-text)",
  MEDIUM: "var(--risk-medium-text)",
  HIGH: "var(--risk-high-text)",
  CRITICAL: "var(--risk-critical-text)",
};

/**
 * ReasoningBar — Layer 2 centrepiece.
 * Full-width, always visible. Shows the complete reasoning chain.
 * "Make it large, readable, always visible." — spec
 * "This one feature answers Layers 2, 3, and 5 simultaneously." — spec
 */
export default function ReasoningBar({ riskLevel, conflictResolution, triggeredSignals, aiEnabled }) {
  const borderColor = riskBorderColor[riskLevel] ?? riskBorderColor.HIGH;
  const textColor = riskTextColor[riskLevel] ?? riskTextColor.HIGH;

  if (!aiEnabled) {
    return (
      <div className="reasoning-bar" style={{ borderTopColor: "var(--color-border)" }}>
        <span className="reasoning-label" style={{ color: "var(--color-text-muted)" }}>AI OFF ▸</span>
        <span className="reasoning-text" style={{ color: "var(--color-text-muted)" }}>
          AI assistance disabled. Operator working independently. Transcript still active.
        </span>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={conflictResolution}
        className="reasoning-bar"
        style={{ borderTopColor: borderColor }}
        initial={{ opacity: 0, y: -4 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <span className="reasoning-label" style={{ color: textColor, flexShrink: 0 }}>
          {riskLevel} ▸
        </span>
        {/* Full reasoning text — no truncation, scrolls if needed */}
        <span className="reasoning-text" title={conflictResolution}>
          {conflictResolution}
        </span>
        {triggeredSignals?.length > 0 && (
          <span className="reasoning-signals" style={{ flexShrink: 0 }}>
            · {triggeredSignals.slice(0, 2).join(" · ")}
          </span>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
