import { motion } from "framer-motion";

const actionColor = { ACCEPT: "var(--verdict-low)", MODIFY: "var(--verdict-medium)", REJECT: "var(--verdict-high)" };
const riskColor = { LOW: "var(--verdict-low)", MEDIUM: "var(--verdict-medium)", HIGH: "var(--verdict-high)", CRITICAL: "var(--risk-critical-text)" };

/**
 * SupervisorDashboard — Layer 4: Longitudinal Pattern Intelligence.
 * Shows systemic trends, operator action patterns, resource gaps.
 * Accessed via [S] key or header button.
 */
export default function SupervisorDashboard({ auditLog, onClose }) {
  const total = auditLog.length;
  const accepts = auditLog.filter((e) => e.action === "ACCEPT").length;
  const modifies = auditLog.filter((e) => e.action === "MODIFY").length;
  const rejects = auditLog.filter((e) => e.action === "REJECT").length;
  const highRiskActions = auditLog.filter((e) => e.risk_level === "HIGH" || e.risk_level === "CRITICAL");
  const uncertainActions = auditLog.filter((e) => e.confidence === "UNCERTAIN");
  const resourcesDispatched = auditLog.filter((e) => e.resource_used).map((e) => e.resource_used);

  return (
    <div className="supervisor-shell font-mono">
      <header className="header-bar text-[var(--color-text-secondary)]">
        <span className="font-bold text-[var(--color-text-primary)]">VoiceForward</span>
        <span>|</span>
        <span className="text-[13px] uppercase tracking-[var(--letter-spacing-caps)]">Supervisor Dashboard — Layer 4</span>
        <button
          type="button"
          onClick={onClose}
          className="ml-auto text-[11px] uppercase tracking-[var(--letter-spacing-caps)] px-2 py-1 rounded border border-[var(--color-border)] hover:border-[var(--color-border-strong)] text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
        >
          ← Back to Call [S]
        </button>
      </header>

      <div className="supervisor-body">
        {/* Stats row */}
        <div className="supervisor-stats-row">
          <StatCard label="Total Actions" value={total} color="var(--color-text-primary)" />
          <StatCard label="Accepted" value={accepts} color="var(--verdict-low)" />
          <StatCard label="Modified" value={modifies} color="var(--verdict-medium)" />
          <StatCard label="Rejected" value={rejects} color="var(--verdict-high)" />
          <StatCard label="High/Critical" value={highRiskActions.length} color="var(--risk-high-text)" />
          <StatCard label="Uncertain Conf." value={uncertainActions.length} color="var(--verdict-uncertain)" />
          <StatCard label="Resources Used" value={resourcesDispatched.length} color="var(--risk-medium-text)" />
        </div>

        <div className="supervisor-panels">
          {/* Operator action replay — Layer 5 */}
          <section className="panel-card supervisor-panel">
            <p className="section-label">Operator Action Replay</p>
            <p className="mt-1 text-[11px] text-[var(--color-text-muted)]">
              Full reasoning chain logged for every AI recommendation. DPDPA compliant — no PII stored.
            </p>
            {auditLog.length === 0 ? (
              <p className="mt-4 text-[13px] text-[var(--color-text-muted)]">No actions recorded this session.</p>
            ) : (
              <ul className="mt-3 flex flex-col gap-2 overflow-y-auto" style={{ maxHeight: 340 }}>
                {auditLog.map((entry, i) => (
                  <motion.li
                    key={i}
                    className="rounded border border-[var(--color-border)] bg-[var(--color-bg-input)] px-3 py-2"
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                  >
                    <div className="flex items-center justify-between gap-4">
                      <span className="text-[12px] font-bold uppercase" style={{ color: actionColor[entry.action] }}>
                        {entry.action}
                      </span>
                      <span className="text-[11px]" style={{ color: riskColor[entry.risk_level] ?? "var(--color-text-secondary)" }}>
                        {entry.risk_level} · {entry.risk_score}
                      </span>
                      <span className="text-[11px] text-[var(--color-text-muted)]">
                        {new Date(entry.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="mt-1 text-[11px] text-[var(--color-text-secondary)]">{entry.reasoning}</p>
                    <p className="mt-1 text-[11px] text-[var(--color-text-muted)] italic">"{entry.suggestion}"</p>
                  </motion.li>
                ))}
              </ul>
            )}
          </section>

          {/* Systemic insights — Layer 4 */}
          <section className="panel-card supervisor-panel">
            <p className="section-label">Systemic Insights</p>
            <p className="mt-1 text-[11px] text-[var(--color-text-muted)]">
              Pattern intelligence across call corpus. Learning from outcomes, not individuals.
            </p>
            <div className="mt-4 flex flex-col gap-3">
              <InsightRow
                label="Acceptance rate"
                value={total ? `${Math.round((accepts / total) * 100)}%` : "—"}
                note="Higher = operator trusts AI guidance"
                color="var(--verdict-low)"
              />
              <InsightRow
                label="Modification rate"
                value={total ? `${Math.round((modifies / total) * 100)}%` : "—"}
                note="Operator adapting suggestions — healthy signal"
                color="var(--verdict-medium)"
              />
              <InsightRow
                label="Rejection rate"
                value={total ? `${Math.round((rejects / total) * 100)}%` : "—"}
                note="High rejection = model needs retraining"
                color="var(--verdict-high)"
              />
              <InsightRow
                label="Uncertain confidence events"
                value={uncertainActions.length}
                note="Contradictory signals — review agent calibration"
                color="var(--verdict-uncertain)"
              />
              <InsightRow
                label="Resources dispatched"
                value={resourcesDispatched.length}
                note="Track follow-through rates across calls"
                color="var(--risk-medium-text)"
              />
            </div>

            {resourcesDispatched.length > 0 && (
              <div className="mt-3 rounded border border-[var(--color-border)] bg-[var(--color-bg-input)] px-3 py-3">
                <p className="section-label">Dispatched Resources This Session</p>
                <ul className="mt-2 flex flex-col gap-1">
                  {resourcesDispatched.map((r, i) => (
                    <li key={i} className="text-[12px] text-[var(--color-text-secondary)] flex items-center gap-2">
                      <span style={{ color: "var(--verdict-low)", fontSize: 8 }}>◆</span>{r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="mt-6 rounded border border-[var(--color-border)] bg-[var(--color-bg-input)] px-3 py-3">
              <p className="section-label">Privacy Architecture</p>
              <p className="mt-2 text-[11px] text-[var(--color-text-secondary)]">
                No PII persists beyond session. Caller audio is never stored. Learning happens on
                anonymised outcome patterns only. DPDPA 2023 compliant — right to erasure enforced
                structurally at session end.
              </p>
            </div>

            <div className="mt-3 rounded border border-[var(--color-border)] bg-[var(--color-bg-input)] px-3 py-3">
              <p className="section-label">Longitudinal Model Improvement</p>
              <p className="mt-2 text-[11px] text-[var(--color-text-secondary)]">
                Accepted suggestions with positive outcomes feed back into resource ranking and
                escalation probability models. Rejected suggestions flag for human review.
                Operator modification patterns identify guidance gaps.
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div className="panel-card text-center" style={{ flex: 1 }}>
      <div className="text-[28px] font-bold" style={{ color }}>{value}</div>
      <div className="section-label mt-1">{label}</div>
    </div>
  );
}

function InsightRow({ label, value, note, color }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-[var(--color-border)] pb-2">
      <div>
        <p className="text-[13px] text-[var(--color-text-primary)]">{label}</p>
        <p className="text-[11px] text-[var(--color-text-muted)]">{note}</p>
      </div>
      <span className="text-[20px] font-bold shrink-0" style={{ color }}>{value}</span>
    </div>
  );
}
