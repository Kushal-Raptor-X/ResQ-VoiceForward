import { motion } from "framer-motion";
import { useState } from "react";

const priorityColor = {
  HIGH: "var(--risk-high-text)",
  MEDIUM: "var(--risk-medium-text)",
  LOW: "var(--verdict-low)",
};

/**
 * ResourcePanel — Layer 3: Resource readiness (pre-ranked, one-click action).
 * Layer 4: Tracks which resources were dispatched for longitudinal analysis.
 */
export default function ResourcePanel({ resources, onDispatch }) {
  const [dispatched, setDispatched] = useState(new Set());

  if (!resources?.length) return null;

  const handleDispatch = (label) => {
    setDispatched((prev) => new Set([...prev, label]));
    onDispatch?.(label);
  };

  return (
    <motion.section
      className="panel-card"
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <p className="section-label">Resource Readiness</p>
      <ul className="mt-3 flex flex-col gap-2">
        {resources.map((r, i) => {
          const used = dispatched.has(r.label);
          return (
            <li
              key={i}
              className="flex items-center justify-between rounded border px-3 py-2 gap-2"
              style={{
                borderColor: used ? "var(--color-border-strong)" : "var(--color-border)",
                background: used ? "var(--color-bg-base)" : "var(--color-bg-input)",
                opacity: used ? 0.6 : 1,
              }}
            >
              <div className="flex items-center gap-2 min-w-0">
                <span style={{ color: priorityColor[r.priority] ?? priorityColor.LOW, fontSize: 8, flexShrink: 0 }}>◆</span>
                <div className="min-w-0">
                  <p className="text-[13px] text-[var(--color-text-primary)] truncate">{r.label}</p>
                  <p className="text-[11px] text-[var(--color-text-muted)] truncate">{r.action}</p>
                </div>
              </div>
              <button
                type="button"
                disabled={used}
                onClick={() => handleDispatch(r.label)}
                className="text-[11px] uppercase tracking-[0.08em] px-2 py-1 rounded border flex-shrink-0 transition-colors"
                style={{
                  borderColor: used ? "var(--color-border)" : priorityColor[r.priority],
                  color: used ? "var(--color-text-muted)" : priorityColor[r.priority],
                  cursor: used ? "default" : "pointer",
                }}
              >
                {used ? "Dispatched ✓" : "Dispatch"}
              </button>
            </li>
          );
        })}
      </ul>
    </motion.section>
  );
}
