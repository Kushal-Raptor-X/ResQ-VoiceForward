export default function NavBar({ activeTab, onTabChange }) {
  const tabs = ["Dashboard", "Live Call", "Call History", "Settings"];

  return (
    <nav className="nav-bar">
      <div className="nav-logo-container">
        <img src="/icons/main icon.png" alt="ResQ VoiceForward" className="nav-logo" />
      </div>
      {tabs.map((tab) => (
        <button
          key={tab}
          className={`nav-tab ${activeTab === tab ? "nav-tab--active" : ""}`}
          onClick={() => onTabChange(tab)}
        >
          {tab}
        </button>
      ))}
    </nav>
  );
}
