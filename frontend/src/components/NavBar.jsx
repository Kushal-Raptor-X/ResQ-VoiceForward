export default function NavBar({ activeTab, onTabChange }) {
  const tabs = ["Dashboard", "Live Call", "Call History", "Settings"];

  return (
    <nav className="nav-bar">
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
