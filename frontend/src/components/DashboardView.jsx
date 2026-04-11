import { MOCK_RECENT_CALLS } from "../mockData";

export default function DashboardView({ analysis, onViewCallHistory }) {
  const riskLevelColor = analysis?.risk_level
    ? `var(--risk-${analysis.risk_level.toLowerCase()}-text)`
    : "var(--color-text-secondary)";

  const getRiskBorderColor = (level) => {
    const levelMap = {
      LOW: "var(--risk-low-border)",
      MEDIUM: "var(--risk-medium-border)",
      HIGH: "var(--risk-high-border)",
      CRITICAL: "var(--risk-critical-border)",
    };
    return levelMap[level] || "var(--color-border)";
  };

  const getRiskTextColor = (level) => {
    const levelMap = {
      LOW: "var(--risk-low-text)",
      MEDIUM: "var(--risk-medium-text)",
      HIGH: "var(--risk-high-text)",
      CRITICAL: "var(--risk-critical-text)",
    };
    return levelMap[level] || "var(--color-text-secondary)";
  };

  return (
    <div className="dashboard-view">
      <div className="metrics-row">
        <div className="panel-card">
          <div className="section-label">Today's Calls</div>
          <div className="metric-value">12</div>
        </div>

        <div className="panel-card">
          <div className="section-label">Active Risk Level</div>
          <div className="metric-value" style={{ color: riskLevelColor }}>
            {analysis?.risk_level ?? "—"}
          </div>
        </div>

        <div className="panel-card">
          <div className="section-label">Avg. Call Duration</div>
          <div className="metric-value">00:06:42</div>
        </div>
      </div>

      <div className="panel-card">
        <div className="section-label" style={{ marginBottom: "var(--space-4)" }}>Recent Calls</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1.5fr 1.2fr 1fr", gap: "var(--space-6)", fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "var(--letter-spacing-caps)", marginBottom: "var(--space-3)" }}>
          <div>Operator</div>
          <div>Caller ID</div>
          <div>Duration</div>
          <div>Language</div>
          <div>Risk</div>
          <div>Score</div>
        </div>
        <div>
          {MOCK_RECENT_CALLS.map((call) => (
            <div key={call.id} style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1.5fr 1.2fr 1fr", gap: "var(--space-6)", alignItems: "center", padding: "var(--space-3) 0", borderBottom: "1px solid var(--color-border)", fontSize: "var(--font-size-sm)" }}>
              <span>{call.operator}</span>
              <span style={{ color: "var(--color-text-secondary)" }}>{call.callerId}</span>
              <span>{call.duration}</span>
              <span style={{ color: "var(--color-text-secondary)" }}>{call.language}</span>
              <span
                style={{
                  border: `1px solid ${getRiskBorderColor(call.riskLevel)}`,
                  color: getRiskTextColor(call.riskLevel),
                  borderRadius: "4px",
                  padding: "2px 8px",
                  fontSize: "var(--font-size-xs)",
                  fontWeight: "var(--font-weight-bold)",
                  letterSpacing: "var(--letter-spacing-caps)",
                  textAlign: "center",
                  display: "inline-block",
                }}
              >
                {call.riskLevel}
              </span>
              <span style={{ color: getRiskTextColor(call.riskLevel), fontWeight: "var(--font-weight-bold)" }}>{call.riskScore}</span>
            </div>
          ))}
        </div>
        <button
          onClick={onViewCallHistory}
          style={{
            background: "transparent",
            border: "1px solid var(--color-border-strong)",
            borderRadius: "4px",
            color: "var(--color-text-primary)",
            cursor: "pointer",
            fontFamily: "var(--font-ui)",
            fontSize: "var(--font-size-xs)",
            fontWeight: "var(--font-weight-medium)",
            letterSpacing: "var(--letter-spacing-caps)",
            marginTop: "var(--space-4)",
            padding: "var(--space-3) var(--space-4)",
            textTransform: "uppercase",
            transition: "background-color 0.15s ease, border-color 0.15s ease",
            width: "fit-content",
          }}
          onMouseEnter={(e) => {
            e.target.style.background = "var(--color-bg-panel-hover)";
            e.target.style.borderColor = "var(--color-text-secondary)";
          }}
          onMouseLeave={(e) => {
            e.target.style.background = "transparent";
            e.target.style.borderColor = "var(--color-border-strong)";
          }}
        >
          View Call History
        </button>
      </div>
    </div>
  );
}
