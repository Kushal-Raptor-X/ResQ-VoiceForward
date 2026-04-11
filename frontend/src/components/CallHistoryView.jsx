export default function CallHistoryView() {
  const mockCallHistory = [
    {
      id: "VF-20256411-001",
      date: "2025-04-11",
      time: "08:15",
      operator: "Priya",
      duration: "14:32",
      language: "Hindi/English",
      aiActions: ["4▲", "1▼", "0✗"],
      outcome: "Referred to counselor",
      peakRisk: "CRITICAL",
      finalRisk: "HIGH",
    },
    {
      id: "VF-20256411-002",
      date: "2025-04-11",
      time: "10:42",
      operator: "Arjun",
      duration: "08:15",
      language: "Kannada",
      aiActions: ["2▲", "0▼", "1✗"],
      outcome: "Resolved — emotional support",
      peakRisk: "MEDIUM",
      finalRisk: "LOW",
    },
    {
      id: "VF-20256411-003",
      date: "2025-04-11",
      time: "11:18",
      operator: "Sneha",
      duration: "22:00",
      language: "English",
      aiActions: ["6▲", "2▼", "1✗"],
      outcome: "Follow up scheduled",
      peakRisk: "HIGH",
      finalRisk: "MEDIUM",
    },
    {
      id: "VF-20256410-004",
      date: "2025-04-10",
      time: "23:12",
      operator: "Rahul",
      duration: "05:44",
      language: "Hindi",
      aiActions: ["2▲", "0▼", "0✗"],
      outcome: "Information provided",
      peakRisk: "LOW",
      finalRisk: "LOW",
    },
    {
      id: "VF-20256410-005",
      date: "2025-04-10",
      time: "01:20",
      operator: "Priya",
      duration: "31:12",
      language: "Hindi/English",
      aiActions: ["8▲", "1▼", "0✗"],
      outcome: "Emergency services dispatched",
      peakRisk: "CRITICAL",
      finalRisk: "CRITICAL",
    },
  ];

  const getRiskColor = (level) => {
    const colorMap = {
      LOW: "var(--risk-low-text)",
      MEDIUM: "var(--risk-medium-text)",
      HIGH: "var(--risk-high-text)",
      CRITICAL: "var(--risk-critical-text)",
    };
    return colorMap[level] || "var(--color-text-secondary)";
  };

  const getRiskBorderColor = (level) => {
    const colorMap = {
      LOW: "var(--risk-low-border)",
      MEDIUM: "var(--risk-medium-border)",
      HIGH: "var(--risk-high-border)",
      CRITICAL: "var(--risk-critical-border)",
    };
    return colorMap[level] || "var(--color-border)";
  };

  return (
    <div className="dashboard-view">
      <div className="panel-card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-4)" }}>
          <div className="section-label">Call History</div>
          <input
            type="text"
            placeholder="Search calls..."
            style={{
              background: "var(--color-bg-input)",
              border: "1px solid var(--color-border)",
              borderRadius: "4px",
              color: "var(--color-text-primary)",
              fontFamily: "var(--font-ui)",
              fontSize: "var(--font-size-sm)",
              padding: "var(--space-2) var(--space-3)",
              width: "300px",
            }}
          />
        </div>
        <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", marginBottom: "var(--space-4)" }}>
          Showing page calls with full AI audit trail
        </div>
        <div>
          {mockCallHistory.map((call) => (
            <div
              key={call.id}
              style={{
                background: "var(--color-bg-base)",
                border: "1px solid var(--color-border)",
                borderRadius: "4px",
                marginBottom: "var(--space-3)",
                padding: "var(--space-4)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-3)" }}>
                <div>
                  <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)", marginBottom: "var(--space-1)" }}>
                    {call.id} — {call.date} at {call.time}
                  </div>
                  <div style={{ fontSize: "var(--font-size-base)", fontWeight: "var(--font-weight-medium)" }}>
                    Operator: {call.operator}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "var(--space-2)" }}>
                  <span
                    style={{
                      background: "var(--risk-high-bg)",
                      border: "1px solid var(--risk-high-border)",
                      borderRadius: "4px",
                      color: "var(--risk-high-text)",
                      fontSize: "var(--font-size-xs)",
                      fontWeight: "var(--font-weight-bold)",
                      letterSpacing: "var(--letter-spacing-caps)",
                      padding: "2px 8px",
                      textTransform: "uppercase",
                    }}
                  >
                    PEAK: {call.peakRisk}
                  </span>
                  <span
                    style={{
                      background: "var(--color-bg-panel)",
                      border: `1px solid ${getRiskBorderColor(call.finalRisk)}`,
                      borderRadius: "4px",
                      color: getRiskColor(call.finalRisk),
                      fontSize: "var(--font-size-xs)",
                      fontWeight: "var(--font-weight-bold)",
                      letterSpacing: "var(--letter-spacing-caps)",
                      padding: "2px 8px",
                      textTransform: "uppercase",
                    }}
                  >
                    FINAL: {call.finalRisk}
                  </span>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "var(--space-4)", fontSize: "var(--font-size-sm)" }}>
                <div>
                  <div className="section-label" style={{ marginBottom: "var(--space-1)" }}>Duration</div>
                  <div>{call.duration}</div>
                </div>
                <div>
                  <div className="section-label" style={{ marginBottom: "var(--space-1)" }}>Language</div>
                  <div>{call.language}</div>
                </div>
                <div>
                  <div className="section-label" style={{ marginBottom: "var(--space-1)" }}>AI Actions</div>
                  <div style={{ display: "flex", gap: "var(--space-2)", fontSize: "var(--font-size-base)" }}>
                    <span style={{ color: "var(--risk-low-text)" }}>{call.aiActions[0]}</span>
                    <span style={{ color: "var(--risk-medium-text)" }}>{call.aiActions[1]}</span>
                    <span style={{ color: "var(--risk-high-text)" }}>{call.aiActions[2]}</span>
                  </div>
                </div>
                <div>
                  <div className="section-label" style={{ marginBottom: "var(--space-1)" }}>Outcome</div>
                  <div>{call.outcome}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
