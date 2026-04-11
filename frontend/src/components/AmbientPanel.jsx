import { motion, AnimatePresence } from "framer-motion";

/**
 * AmbientPanel — Layer 1: Ambient audio classification.
 * Shows background audio signals that affect the risk model
 * even when the caller doesn't explicitly mention them.
 */
export default function AmbientPanel({ signals }) {
  if (!signals?.length) return null;

  return (
    <motion.section
      className="panel-card"
      style={{ borderLeft: "3px solid var(--risk-medium-border)" }}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center gap-2">
        <span aria-hidden="true">🎙</span>
        <p className="section-label text-[var(--color-text-primary)]">Ambient Audio Signals</p>
      </div>
      <AnimatePresence>
        <ul className="mt-2 flex flex-col gap-1">
          {signals.map((signal, i) => (
            <motion.li
              key={signal}
              className="flex items-start gap-2 text-[12px]"
              initial={{ opacity: 0, x: -4 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <span style={{ color: "var(--risk-medium-text)", fontSize: 8, marginTop: 4 }}>◆</span>
              <span style={{ color: "var(--risk-medium-text)" }}>{signal}</span>
            </motion.li>
          ))}
        </ul>
      </AnimatePresence>
      <p className="mt-2 text-[11px] text-[var(--color-text-muted)]">
        Ambient context incorporated into risk model
      </p>
    </motion.section>
  );
}
