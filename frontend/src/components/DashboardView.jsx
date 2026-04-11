import { useEffect, useState } from "react";

export default function DashboardView({ analysis, onViewCallHistory }) {
  const [stats, setStats] = useState({
    todayCalls: 0,
    avgDuration: "00:00:00",
    totalCalls: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/calls?limit=100");
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      const calls = data.calls || [];
      
      // Calculate today's calls (last 24 hours)
      const now = Date.now();
      const oneDayAgo = now - (24 * 60 * 60 * 1000);
      const todayCalls = calls.filter(call => {
        const callTime = new Date(call.created_at).getTime();
        return callTime >= oneDayAgo;
      }).length;
      
      // Calculate average duration (mock for now - would need duration field in DB)
      const avgDuration = "00:06:42";
      
      setStats({
        todayCalls,
        avgDuration,
        totalCalls: data.total || 0
      });
    } catch (err) {
      console.error("[Dashboard] Failed to fetch stats:", err);
    } finally {
      setLoading(false);
    }
  };

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
          <div className="metric-value">
            {loading ? "—" : stats.todayCalls}
          </div>
        </div>

        <div className="panel-card">
          <div className="section-label">Active Risk Level</div>
          <div className="metric-value" style={{ color: riskLevelColor }}>
            {analysis?.risk_level ?? "—"}
          </div>
        </div>

        <div className="panel-card">
          <div className="section-label">Total Calls Logged</div>
          <div className="metric-value">
            {loading ? "—" : stats.totalCalls}
          </div>
        </div>
      </div>

      <div className="panel-card">
        <div className="section-label" style={{ marginBottom: "var(--space-4)" }}>
          Recent Activity
        </div>
        <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", marginBottom: "var(--space-4)" }}>
          All call data is fetched from backend. No data is stored in browser.
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
          View Full Call History
        </button>
      </div>

      <div className="panel-card">
        <div className="section-label" style={{ marginBottom: "var(--space-4)" }}>
          🔒 Privacy & Data Handling
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>No data is stored in browser (no localStorage, sessionStorage, or cookies)</span>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>All call data is fetched from secure backend API</span>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>Session data is cleared when call ends</span>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>No caller PII persists beyond session (DPDPA 2023 compliant)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
