const actions = [
  { label: "Accept", onClickKey: "onAccept", bg: "var(--btn-accept-bg)", border: "var(--btn-accept-border)", text: "var(--btn-accept-text)" },
  { label: "Modify", onClickKey: "onModify", bg: "var(--btn-modify-bg)", border: "var(--btn-modify-border)", text: "var(--btn-modify-text)" },
  { label: "Reject", onClickKey: "onReject", bg: "var(--btn-reject-bg)", border: "var(--btn-reject-border)", text: "var(--btn-reject-text)" },
];

export default function SuggestionCard(props) {
  return (
    <section className="panel-card">
      <p className="section-label">Suggested Response</p>
      <blockquote className="quote-box mt-3">{props.suggestedResponse}</blockquote>
      <div className="mt-4">
        <p className="section-label">Operator Note:</p>
        <p className="mt-2 text-sm text-[var(--color-text-secondary)]">{props.operatorNote}</p>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-3">
        {actions.map((action) => (
          <button
            key={action.label}
            type="button"
            className="action-button"
            onClick={props[action.onClickKey]}
            style={{
              "--button-bg": action.bg,
              "--button-border": action.border,
              "--button-text": action.text,
            }}
          >
            {action.label}
          </button>
        ))}
      </div>
      <div className="mt-4 min-h-10 rounded-lg border border-[var(--color-border)] px-3 py-2">
        <p className="section-label">Layer 5 Audit</p>
        <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
          {props.lastAction
            ? `${props.lastAction.action} recorded at ${props.lastAction.timestamp}`
            : "No operator action recorded yet."}
        </p>
      </div>
    </section>
  );
}
