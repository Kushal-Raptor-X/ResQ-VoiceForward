import { useEffect, useState } from "react";

export default function CallHistoryView() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [storage, setStorage] = useState("unknown");

  useEffect(() => {
    fetchCalls();
  }, []);

  const fetchCalls = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log("[CallHistory] Fetching calls from backend...");
      const response = await fetch("http://localhost:8000/calls?limit=50");
      
      console.log("[CallHistory] Response status:", response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log("[CallHistory] Received data:", data);
      
      if (data.error) {
        setError(data.error);
        console.error("[CallHistory] API returned error:", data.error);
      } else {
        setCalls(data.calls || []);
        setStorage(data.storage || "unknown");
        console.log(`[CallHistory] Loaded ${data.calls?.length || 0} calls from ${data.storage}`);
      }
    } catch (err) {
      console.error("[CallHistory] Fetch error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteCall = async (callId) => {
    if (!confirm("Are you sure you want to delete this call log?")) return;
    
    try {
      const response = await fetch(`http://localhost:8000/calls/${callId}`, {
        method: "DELETE",
      });
      const data = await response.json();
      
      if (data.success) {
        // Remove from local state
        setCalls(calls.filter(call => call._id !== callId));
      } else {
        alert(`Failed to delete: ${data.error}`);
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const deleteAllCalls = async () => {
    if (!confirm("⚠️ WARNING: This will delete ALL call logs. Are you sure?")) return;
    if (!confirm("This action cannot be undone. Continue?")) return;
    
    try {
      const response = await fetch("http://localhost:8000/calls", {
        method: "DELETE",
      });
      const data = await response.json();
      
      if (data.success) {
        setCalls([]);
        alert(`Deleted ${data.deleted_count} calls`);
      } else {
        alert(`Failed to delete: ${data.error}`);
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const formatDuration = (createdAt) => {
    if (!createdAt) return "N/A";
    const date = new Date(createdAt);
    return date.toLocaleString();
  };

  const filteredCalls = calls.filter(call => 
    searchQuery === "" || 
    call.session_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    call.risk_level?.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
          <div className="section-label">Call History ({storage})</div>
          <div style={{ display: "flex", gap: "var(--space-3)" }}>
            <input
              type="text"
              placeholder="Search calls..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: "var(--color-bg-input)",
                border: "1px solid var(--color-border)",
                borderRadius: "4px",
                color: "var(--color-text-primary)",
                fontFamily: "var(--font-ui)",
                fontSize: "var(--font-size-sm)",
                padding: "var(--space-2) var(--space-3)",
                width: "200px",
              }}
            />
            <button
              onClick={fetchCalls}
              style={{
                background: "var(--color-bg-panel)",
                border: "1px solid var(--verdict-low)",
                borderRadius: "4px",
                color: "var(--verdict-low)",
                cursor: "pointer",
                fontFamily: "var(--font-ui)",
                fontSize: "var(--font-size-sm)",
                padding: "var(--space-2) var(--space-3)",
              }}
            >
              Refresh
            </button>
            <button
              onClick={deleteAllCalls}
              style={{
                background: "var(--btn-reject-bg)",
                border: "1px solid var(--risk-high-border)",
                borderRadius: "4px",
                color: "var(--risk-high-text)",
                cursor: "pointer",
                fontFamily: "var(--font-ui)",
                fontSize: "var(--font-size-sm)",
                padding: "var(--space-2) var(--space-3)",
              }}
            >
              Delete All
            </button>
          </div>
        </div>
        
        {loading && (
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", padding: "var(--space-4)" }}>
            Loading call history...
          </div>
        )}
        
        {error && (
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--risk-high-text)", padding: "var(--space-4)" }}>
            Error: {error}
          </div>
        )}
        
        {!loading && !error && filteredCalls.length === 0 && calls.length > 0 && (
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--risk-medium-text)", padding: "var(--space-4)" }}>
            No calls match your search query. Clear search to see all {calls.length} calls.
          </div>
        )}
        
        {!loading && !error && calls.length === 0 && (
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", padding: "var(--space-4)" }}>
            No call logs found. Start a call to begin logging.
          </div>
        )}
        
        <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", marginBottom: "var(--space-4)" }}>
          Showing {filteredCalls.length} calls with full AI audit trail
        </div>
        
        <div>
          {filteredCalls.map((call) => (
            <div
              key={call._id}
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
                    {call.session_id} — {formatDuration(call.created_at)}
                  </div>
                  <div style={{ fontSize: "var(--font-size-base)", fontWeight: "var(--font-weight-medium)" }}>
                    Confidence: {call.confidence || "N/A"}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "var(--space-2)" }}>
                  <span
                    style={{
                      background: `var(--risk-${call.risk_level?.toLowerCase()}-bg)`,
                      border: `1px solid var(--risk-${call.risk_level?.toLowerCase()}-border)`,
                      borderRadius: "4px",
                      color: `var(--risk-${call.risk_level?.toLowerCase()}-text)`,
                      fontSize: "var(--font-size-xs)",
                      fontWeight: "var(--font-weight-bold)",
                      letterSpacing: "var(--letter-spacing-caps)",
                      padding: "2px 8px",
                      textTransform: "uppercase",
                    }}
                  >
                    {call.risk_level || "UNKNOWN"}
                  </span>
                  <button
                    onClick={() => deleteCall(call._id)}
                    style={{
                      background: "var(--btn-reject-bg)",
                      border: "1px solid var(--risk-high-border)",
                      borderRadius: "4px",
                      color: "var(--risk-high-text)",
                      cursor: "pointer",
                      fontSize: "var(--font-size-xs)",
                      padding: "2px 8px",
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "var(--space-4)", fontSize: "var(--font-size-sm)" }}>
                <div>
                  <div className="section-label" style={{ marginBottom: "var(--space-1)" }}>Triggered Signals</div>
                  <div style={{ fontSize: "var(--font-size-xs)" }}>
                    {call.triggered_signals?.slice(0, 2).join(", ") || "None"}
                  </div>
                </div>
                <div>
                  <div className="section-label" style={{ marginBottom: "var(--space-1)" }}>Operator Action</div>
                  <div>{call.operator_action || "pending"}</div>
                </div>
                <div>
                  <div className="section-label" style={{ marginBottom: "var(--space-1)" }}>Outcome</div>
                  <div>{call.outcome || "unknown"}</div>
                </div>
              </div>
              {call.transcript && (
                <div style={{ marginTop: "var(--space-3)", fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
                  <div className="section-label" style={{ marginBottom: "var(--space-1)" }}>Transcript Preview</div>
                  <div style={{ maxHeight: "60px", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {call.transcript.substring(0, 200)}...
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
