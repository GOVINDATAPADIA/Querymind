import { useState } from 'react';
import { Database, PanelLeftOpen, PanelLeftClose, Sun, Moon, HelpCircle, X, ShieldCheck } from 'lucide-react';
import './Header.css';

function GithubIcon({ size = 17 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
      <path d="M9 18c-4.51 2-5-2-7-2" />
    </svg>
  );
}

function HealthIndicator({ status }) {
  const isConnected = status === 'connected';
  return (
    <div className="health-indicator" title={isConnected ? 'Database & LLM Connected' : 'Connecting to API...'}>
      <span
        className={`health-dot ${isConnected ? 'health-dot--connected' : 'health-dot--offline'}`}
      />
      <span
        className={`health-text ${isConnected ? 'health-text--connected' : 'health-text--offline'}`}
      >
        {isConnected ? 'CONNECTED' : 'OFFLINE'}
      </span>
    </div>
  );
}

function HelpModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="help-modal-backdrop" onClick={onClose}>
      <div className="help-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="help-modal-header">
          <div className="help-modal-title">
            <Database size={18} className="help-modal-icon" />
            <span>QueryMind Architecture & Tips</span>
          </div>
          <button className="help-modal-close" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="help-modal-body">
          <h4>🌟 How to query your database:</h4>
          <ul>
            <li><strong>Aggregations:</strong> <em>"What is the total revenue by category this year?"</em></li>
            <li><strong>Top / Bottom Ranking:</strong> <em>"Show top 5 customers with most orders"</em></li>
            <li><strong>Time Trends:</strong> <em>"Show monthly order volume for the past 6 months"</em></li>
            <li><strong>Cross-Table Joins:</strong> <em>"List products purchased by VIP tier customers"</em></li>
          </ul>

          <div className="help-modal-safety-box">
            <ShieldCheck size={16} className="help-modal-shield" />
            <span>
              <strong>Safe & Read-Only:</strong> QueryMind automatically enforces read-only operations. Any data-modifying queries (DROP, DELETE, UPDATE) are blocked.
            </span>
          </div>
        </div>
      </div>
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
  const [showHelp, setShowHelp] = useState(false);

  return (
    <>
      <header className="header">
        <div className="header-left">
          <button
            className="sidebar-toggle-btn"
            onClick={onToggleSidebar}
            title={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
            aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
          >
            {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
          </button>

          <div className="header-logo">
            <div className="header-logo-icon-wrapper">
              <Database size={20} className="header-logo-icon" />
            </div>
            <span className="header-logo-text">QueryMind</span>
          </div>

          <div className="header-badge">
            <span>PostgreSQL</span>
          </div>
        </div>

        <div className="header-right">
          <HealthIndicator status={healthStatus} />

          <button
            className="header-icon-btn"
            onClick={() => setShowHelp(true)}
            title="Help & Example Queries"
          >
            <HelpCircle size={17} />
          </button>

          <a
            href="https://github.com/GOVINDATAPADIA/Querymind"
            target="_blank"
            rel="noopener noreferrer"
            className="header-icon-btn"
            title="GitHub Repository"
          >
            <GithubIcon size={17} />
          </a>

          <button
            className="theme-toggle-btn"
            onClick={onToggleTheme}
            title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          </button>
        </div>
      </header>

      <HelpModal isOpen={showHelp} onClose={() => setShowHelp(false)} />
    </>
  );
}
