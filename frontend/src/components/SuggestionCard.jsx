const actions = [
  { label: "✓ Accept", hint: "[A]", key: "onAccept", bg: "var(--btn-accept-bg)", border: "var(--btn-accept-border)", text: "var(--btn-accept-text)" },
  { label: "✎ Modify", hint: "[M]", key: "onModify", bg: "var(--btn-modify-bg)", border: "var(--btn-modify-border)", text: "var(--btn-modify-text)" },
  { label: "✗ Reject", hint: "[R]", key: "onReject", bg: "var(--btn-reject-bg)", border: "var(--btn-reject-border)", text: "var(--btn-reject-text)" },
];

export default function SuggestionCard({ suggestedResponse, operatorNote, onAccept, onModify, onReject }) {
  const handlers = { onAccept, onModify, onReject };

  return (
    <section className="panel-card">
      <p className="section-label">What to Say Next</p>
      <blockquote className="quote-box mt-3">{suggestedResponse}</blockquote>

      {operatorNote && (
        <div className="mt-3 rounded border border-[var(--color-border)] bg-[var(--color-bg-input)] px-3 py-2">
          <p className="section-label">Operator Note</p>
          <p className="mt-1 text-[13px] text-[var(--color-text-secondary)]">{operatorNote}</p>
        </div>
      )}

      <div className="mt-4 grid grid-cols-3 gap-2">
        {actions.map((action) => (
          <button
            key={action.label}
            type="button"
            className="action-button"
            onClick={handlers[action.key]}
            style={{
              "--button-bg": action.bg,
              "--button-border": action.border,
              "--button-text": action.text,
            }}
          >
            <span>{action.label}</span>
            <span style={{ display: "block", fontSize: 10, opacity: 0.5, marginTop: 2 }}>{action.hint}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
