const actionColor = {
  ACCEPT: "var(--verdict-low)",
  MODIFY: "var(--verdict-medium)",
  REJECT: "var(--verdict-high)",
};

const actionIcon = {
  ACCEPT: "✓",
  MODIFY: "✎",
  REJECT: "✗",
};

export default function AuditLog({ entries }) {
  return (
    <section className="panel-card">
      <p className="section-label">Layer 5 — Operator Audit Log</p>
      {entries.length === 0 ? (
        <p className="mt-3 text-[13px] text-[var(--color-text-muted)]">No operator actions recorded yet.</p>
      ) : (
        <ul className="mt-3 flex flex-col gap-2 max-h-40 overflow-y-auto pr-1">
          {entries.map((entry, i) => (
            <li
              key={i}
              className="rounded border border-[var(--color-border)] bg-[var(--color-bg-input)] px-3 py-2"
            >
              <div className="flex items-center justify-between">
                <span
                  className="text-[12px] font-bold uppercase tracking-[var(--letter-spacing-caps)]"
                  style={{ color: actionColor[entry.action] }}
                >
                  {actionIcon[entry.action]} {entry.action}
                </span>
                <span className="text-[11px] text-[var(--color-text-muted)]">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="mt-1 text-[11px] text-[var(--color-text-secondary)] truncate">
                Risk: {entry.risk_level} ({entry.risk_score}) · Conf: {entry.confidence}
              </p>
              {entry.reasoning && (
                <p className="mt-1 text-[11px] text-[var(--color-text-muted)] line-clamp-2">
                  {entry.reasoning}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
