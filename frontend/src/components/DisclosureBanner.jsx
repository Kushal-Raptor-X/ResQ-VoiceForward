import { motion } from "framer-motion";

/**
 * DisclosureBanner — Layer 5: DPDPA 2023 compliance.
 * Callers must be informed within the first 30 seconds that AI is assisting.
 * Operator dismisses this after reading the disclosure to the caller.
 */
export default function DisclosureBanner({ onDismiss }) {
  return (
    <motion.div
      className="disclosure-banner"
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <span className="disclosure-icon">🔒</span>
      <span className="disclosure-text">
        <strong>AI DISCLOSURE REQUIRED</strong> — Inform caller within 30 seconds:
        <em> "This call is assisted by an AI system to help me support you better. You can ask me to turn it off at any time."</em>
      </span>
      <button
        type="button"
        className="disclosure-dismiss"
        onClick={onDismiss}
      >
        Disclosed ✓
      </button>
    </motion.div>
  );
}
