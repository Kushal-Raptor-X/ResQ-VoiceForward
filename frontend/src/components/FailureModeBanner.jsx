import { motion } from "framer-motion";

/**
 * FailureModeBanner — Layer 5: Graceful failure mode handling.
 * Each failure mode has a specific designed response, not a generic error.
 *
 * Required cases per ResQ PS:
 * - stt_fail: STT failure causing agents to operate on false information
 * - model_misclassify: Emotion model misclassification (high-risk rated low-risk)
 * - resource_error: Resource dispatch error
 */

const FAILURE_CONFIGS = {
  stt_fail: {
    icon: "🎤",
    title: "STT OFFLINE",
    message:
      "Speech-to-text is unavailable. Agents are operating on the last known transcript. Risk assessment may be stale. Do not rely on AI guidance until STT recovers.",
    action: "Continue manually — trust your training",
    color: "var(--verdict-uncertain)",
    bg: "#1a1500",
    border: "var(--risk-medium-border)",
  },
  model_misclassify: {
    icon: "⚠",
    title: "POSSIBLE MISCLASSIFICATION",
    message:
      "Confidence is UNCERTAIN with elevated risk score. The emotion model may have rated a high-risk caller as lower risk. Conservative protocol applied — treating as HIGH regardless.",
    action: "Verify with your own assessment — do not downgrade risk",
    color: "var(--verdict-uncertain)",
    bg: "#130d1a",
    border: "var(--verdict-uncertain)",
  },
  resource_error: {
    icon: "📵",
    title: "RESOURCE DISPATCH ERROR",
    message:
      "A resource referral could not be completed. Fallback options are shown below. Contact supervisor directly if primary resource is unavailable.",
    action: "Use fallback resources or contact supervisor",
    color: "var(--risk-high-text)",
    bg: "#1a0d0d",
    border: "var(--risk-high-border)",
  },
};

export default function FailureModeBanner({ mode, onDismiss }) {
  const config = FAILURE_CONFIGS[mode];
  if (!config) return null;

  return (
    <motion.div
      className="failure-banner"
      style={{ background: config.bg, borderBottomColor: config.border }}
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <span className="text-[16px] flex-shrink-0">{config.icon}</span>
      <div className="flex-1 min-w-0">
        <span className="text-[11px] font-bold uppercase tracking-[0.08em]" style={{ color: config.color }}>
          {config.title}
        </span>
        <span className="mx-2 text-[var(--color-text-muted)]">—</span>
        <span className="text-[12px] text-[var(--color-text-secondary)]">{config.message}</span>
        <span className="mx-2 text-[var(--color-text-muted)]">·</span>
        <span className="text-[12px] font-bold" style={{ color: config.color }}>{config.action}</span>
      </div>
      <button
        type="button"
        onClick={onDismiss}
        className="text-[11px] uppercase tracking-[0.08em] px-2 py-1 rounded border flex-shrink-0"
        style={{ borderColor: config.border, color: config.color }}
      >
        Dismiss
      </button>
    </motion.div>
  );
}
