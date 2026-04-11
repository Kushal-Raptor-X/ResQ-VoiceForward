import { motion } from "framer-motion";

const agents = [
  { key: "language_agent", icon: "🗣", label: "Language Agent", delay: 0 },
  { key: "emotion_agent", icon: "🎭", label: "Emotion Agent", delay: 0.15 },
  { key: "risk_agent", icon: "⚠", label: "Risk Agent", delay: 0.3 },
  { key: "context_agent", icon: "🧠", label: "Context Agent", delay: 0.45 },
];

const verdictColors = {
  LOW: "var(--verdict-low)",
  MEDIUM: "var(--verdict-medium)",
  HIGH: "var(--verdict-high)",
  CRITICAL: "var(--verdict-high)",
  UNCERTAIN: "var(--verdict-uncertain)",
};

const parseBreakdown = (value = "UNCERTAIN - Awaiting analysis.") => {
  const idx = value.indexOf(" - ");
  if (idx === -1) return { verdict: "UNCERTAIN", reasoning: value };
  return {
    verdict: value.slice(0, idx).toUpperCase(),
    reasoning: value.slice(idx + 3),
  };
};

export default function AgentPanel({ agentBreakdown, conflict, conflictResolution }) {
  return (
    <section className="flex flex-col gap-2">
      <p className="section-label px-1">Multi-Agent Breakdown</p>

      {agents.map((agent) => {
        const { verdict, reasoning } = parseBreakdown(agentBreakdown?.[agent.key]);
        const badgeColor = verdictColors[verdict] ?? verdictColors.UNCERTAIN;
        return (
          <motion.div
            key={agent.key}
            className="panel-card"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: agent.delay, ease: "easeOut" }}
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span aria-hidden="true" className="text-base">{agent.icon}</span>
                <span className="section-label text-[var(--color-text-primary)]">{agent.label}</span>
              </div>
              <span
                className="agent-badge"
                style={{ "--badge-color": badgeColor }}
              >
                {verdict}
              </span>
            </div>
            <p className="mt-2 text-[13px] text-[var(--color-text-secondary)]">{reasoning}</p>
          </motion.div>
        );
      })}

      {/* Conflict card */}
      <motion.div
        className="panel-card"
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2, delay: 0.65, ease: "easeOut" }}
        style={{ borderLeft: "3px solid var(--verdict-uncertain)" }}
      >
        <p className="section-label text-[var(--color-text-primary)]">Conflict Detection</p>
        <p className="mt-2 text-[13px] text-[var(--color-text-secondary)]">{conflict}</p>
        {conflictResolution && (
          <>
            <p className="section-label mt-3 text-[var(--color-text-primary)]">Resolution Reasoning</p>
            <p className="mt-2 text-[13px]" style={{ color: "var(--verdict-uncertain)" }}>
              {conflictResolution}
            </p>
          </>
        )}
      </motion.div>
    </section>
  );
}
