export default function SettingsView() {
  return (
    <div className="dashboard-view">
      <div style={{ marginBottom: "var(--space-6)" }}>
        <h1 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-bold)", marginBottom: "var(--space-2)" }}>
          SETTINGS
        </h1>
        <p style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)" }}>
          System configuration and operator preferences
        </p>
      </div>

      {/* Operator Profile */}
      <div className="panel-card" style={{ marginBottom: "var(--space-4)" }}>
        <div className="section-label" style={{ marginBottom: "var(--space-4)" }}>
          OPERATOR PROFILE
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-6)" }}>
          <div>
            <label style={{ display: "block", color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)", marginBottom: "var(--space-2)", textTransform: "uppercase", letterSpacing: "var(--letter-spacing-caps)" }}>
              Name
            </label>
            <input
              type="text"
              defaultValue="Priya Sharma"
              style={{
                background: "var(--color-bg-input)",
                border: "1px solid var(--color-border)",
                borderRadius: "4px",
                color: "var(--color-text-primary)",
                fontFamily: "var(--font-ui)",
                fontSize: "var(--font-size-sm)",
                padding: "var(--space-3)",
                width: "100%",
              }}
            />
          </div>
          <div>
            <label style={{ display: "block", color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)", marginBottom: "var(--space-2)", textTransform: "uppercase", letterSpacing: "var(--letter-spacing-caps)" }}>
              Role
            </label>
            <input
              type="text"
              defaultValue="Senior Operator"
              style={{
                background: "var(--color-bg-input)",
                border: "1px solid var(--color-border)",
                borderRadius: "4px",
                color: "var(--color-text-primary)",
                fontFamily: "var(--font-ui)",
                fontSize: "var(--font-size-sm)",
                padding: "var(--space-3)",
                width: "100%",
              }}
            />
          </div>
          <div>
            <label style={{ display: "block", color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)", marginBottom: "var(--space-2)", textTransform: "uppercase", letterSpacing: "var(--letter-spacing-caps)" }}>
              Languages
            </label>
            <input
              type="text"
              defaultValue="Hindi, English, Marathi"
              style={{
                background: "var(--color-bg-input)",
                border: "1px solid var(--color-border)",
                borderRadius: "4px",
                color: "var(--color-text-primary)",
                fontFamily: "var(--font-ui)",
                fontSize: "var(--font-size-sm)",
                padding: "var(--space-3)",
                width: "100%",
              }}
            />
          </div>
          <div>
            <label style={{ display: "block", color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)", marginBottom: "var(--space-2)", textTransform: "uppercase", letterSpacing: "var(--letter-spacing-caps)" }}>
              Shift
            </label>
            <input
              type="text"
              defaultValue="09:00 - 21:00 IST"
              style={{
                background: "var(--color-bg-input)",
                border: "1px solid var(--color-border)",
                borderRadius: "4px",
                color: "var(--color-text-primary)",
                fontFamily: "var(--font-ui)",
                fontSize: "var(--font-size-sm)",
                padding: "var(--space-3)",
                width: "100%",
              }}
            />
          </div>
        </div>
      </div>

      {/* AI Behavior */}
      <div className="panel-card" style={{ marginBottom: "var(--space-4)" }}>
        <div className="section-label" style={{ marginBottom: "var(--space-4)" }}>
          ⚙ AI BEHAVIOR
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)" }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-2)" }}>
              <div>
                <div style={{ fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-medium)" }}>
                  Risk Sensitivity
                </div>
                <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)" }}>
                  How aggressively the system flags risk
                </div>
              </div>
              <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)" }}>
                Conservative (Default)
              </div>
            </div>
          </div>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-2)" }}>
              <div>
                <div style={{ fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-medium)" }}>
                  Suggestion Frequency
                </div>
                <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)" }}>
                  How often AI generates response suggestions
                </div>
              </div>
              <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)" }}>
                On every risk change
              </div>
            </div>
          </div>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-2)" }}>
              <div>
                <div style={{ fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-medium)" }}>
                  Conflict Resolution
                </div>
                <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)" }}>
                  How agent disagreements are resolved
                </div>
              </div>
              <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)" }}>
                Default to highest risk
              </div>
            </div>
          </div>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-2)" }}>
              <div>
                <div style={{ fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-medium)" }}>
                  Confidence Threshold
                </div>
                <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)" }}>
                  Minimum confidence before showing suggestions
                </div>
              </div>
              <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)" }}>
                60%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Keyboard Shortcuts */}
      <div className="panel-card" style={{ marginBottom: "var(--space-4)" }}>
        <div className="section-label" style={{ marginBottom: "var(--space-4)" }}>
          ⌨ KEYBOARD SHORTCUTS
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "var(--space-2) 0" }}>
            <span style={{ fontSize: "var(--font-size-sm)" }}>Accept suggestion</span>
            <kbd style={{ background: "var(--color-bg-input)", border: "1px solid var(--color-border)", borderRadius: "4px", padding: "2px 8px", fontSize: "var(--font-size-xs)", fontFamily: "var(--font-ui)" }}>A</kbd>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "var(--space-2) 0" }}>
            <span style={{ fontSize: "var(--font-size-sm)" }}>Modify suggestion</span>
            <kbd style={{ background: "var(--color-bg-input)", border: "1px solid var(--color-border)", borderRadius: "4px", padding: "2px 8px", fontSize: "var(--font-size-xs)", fontFamily: "var(--font-ui)" }}>M</kbd>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "var(--space-2) 0" }}>
            <span style={{ fontSize: "var(--font-size-sm)" }}>Reject suggestion</span>
            <kbd style={{ background: "var(--color-bg-input)", border: "1px solid var(--color-border)", borderRadius: "4px", padding: "2px 8px", fontSize: "var(--font-size-xs)", fontFamily: "var(--font-ui)" }}>R</kbd>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "var(--space-2) 0" }}>
            <span style={{ fontSize: "var(--font-size-sm)" }}>Toggle call recording</span>
            <kbd style={{ background: "var(--color-bg-input)", border: "1px solid var(--color-border)", borderRadius: "4px", padding: "2px 8px", fontSize: "var(--font-size-xs)", fontFamily: "var(--font-ui)" }}>Space</kbd>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "var(--space-2) 0" }}>
            <span style={{ fontSize: "var(--font-size-sm)" }}>Dismiss alert</span>
            <kbd style={{ background: "var(--color-bg-input)", border: "1px solid var(--color-border)", borderRadius: "4px", padding: "2px 8px", fontSize: "var(--font-size-xs)", fontFamily: "var(--font-ui)" }}>Esc</kbd>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "var(--space-2) 0" }}>
            <span style={{ fontSize: "var(--font-size-sm)" }}>Next panel</span>
            <kbd style={{ background: "var(--color-bg-input)", border: "1px solid var(--color-border)", borderRadius: "4px", padding: "2px 8px", fontSize: "var(--font-size-xs)", fontFamily: "var(--font-ui)" }}>Tab</kbd>
          </div>
        </div>
      </div>

      {/* Privacy & Compliance */}
      <div className="panel-card">
        <div className="section-label" style={{ marginBottom: "var(--space-4)" }}>
          🔒 PRIVACY & COMPLIANCE
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>No caller PII persists beyond session (DPDPA 2023 compliant)</span>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>All AI recommendations are logged immutably with full reasoning chain</span>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>Operator actions (accept/modify/reject) recorded for audit trail</span>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>Data localisation: all processing within Indian infrastructure</span>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "var(--space-2)" }}>
            <span>•</span>
            <span>Right to erasure: session data can be purged on request</span>
          </div>
        </div>
      </div>
    </div>
  );
}
