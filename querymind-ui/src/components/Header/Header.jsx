import { Database, PanelLeftOpen, PanelLeftClose, Sun, Moon } from 'lucide-react';
import './Header.css';

function HealthIndicator({ status }) {
  const isConnected = status === 'connected';
  return (
    <div className="health-indicator">
      <span
        className={`health-dot ${isConnected ? 'health-dot--connected' : 'health-dot--offline'}`}
      />
      <span
        className={`health-text ${isConnected ? 'health-text--connected' : 'health-text--offline'}`}
      >
        {isConnected ? 'Connected' : 'Offline'}
      </span>
    </div>
  );
}

export default function Header({
  healthStatus,
  onToggleTheme,
  theme,
  onToggleSidebar,
  sidebarOpen,
}) {
  return (
    <header className="header">
      <div className="header-left">
        <button
          className="sidebar-toggle-btn"
          onClick={onToggleSidebar}
          title={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
          aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
        >
          {sidebarOpen ? <PanelLeftClose size={20} /> : <PanelLeftOpen size={20} />}
        </button>

        <div className="header-logo">
          <Database size={24} className="header-logo-icon" />
          <span className="header-logo-text">QueryMind</span>
        </div>
      </div>

      <div className="header-right">
        <HealthIndicator status={healthStatus} />

        <button
          className="theme-toggle-btn"
          onClick={onToggleTheme}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
