import { motion } from "framer-motion";

const agents = [
  { key: "language_agent", icon: "🗣", label: "Language Agent", delay: 0 },
  { key: "emotion_agent", icon: "🎭", label: "Emotion Agent", delay: 0.2 },
  { key: "narrative_agent", icon: "📖", label: "Narrative Agent", delay: 0.4 },
];

const verdictColors = {
  LOW: "var(--verdict-low)",
  MEDIUM: "var(--verdict-medium)",
  HIGH: "var(--verdict-high)",
  CRITICAL: "var(--verdict-high)",
  UNCERTAIN: "var(--verdict-uncertain)",
};

const parseBreakdown = (value = "UNCERTAIN - Awaiting analysis.") => {
  const [verdict, ...reasoning] = value.split(" - ");
  return { verdict: verdict.toUpperCase(), reasoning: reasoning.join(" - ") || value };
};

export default function AgentPanel({ agentBreakdown, conflict }) {
  return (
    <section className="flex flex-col gap-3">
      {agents.map((agent) => {
        const breakdown = parseBreakdown(agentBreakdown?.[agent.key]);
        return (
          <motion.div
            key={agent.key}
            className="panel-card"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: agent.delay, ease: "easeOut" }}
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <span aria-hidden="true">{agent.icon}</span>
                <span className="section-label text-[var(--color-text-primary)]">{agent.label}</span>
              </div>
              <span className="agent-badge" style={{ "--badge-color": verdictColors[breakdown.verdict] ?? verdictColors.UNCERTAIN }}>
                {breakdown.verdict}
              </span>
            </div>
            <p className="mt-3 text-sm text-[var(--color-text-secondary)]">{breakdown.reasoning}</p>
          </motion.div>
        );
      })}
      <motion.div
        className="panel-card"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2, delay: 0.7, ease: "easeOut" }}
        style={{ borderLeft: "3px solid var(--verdict-uncertain)" }}
      >
        <p className="section-label text-[var(--color-text-primary)]">Conflict Resolution</p>
        <p className="mt-3 text-sm text-[var(--color-text-secondary)]">{conflict}</p>
      </motion.div>
    </section>
  );
}
