import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header/Header';
import Sidebar from './components/Sidebar/Sidebar';
import ChatInterface from './components/ChatInterface/ChatInterface';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  // ── State ────────────────────────────────────
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('querymind-theme') || 'dark';
  });
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarTab, setSidebarTab] = useState('schema');
  const [messages, setMessages] = useState([]);
  const [schema, setSchema] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);

  // ── Theme Toggle ─────────────────────────────
  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark';
      localStorage.setItem('querymind-theme', next);
      return next;
    });
  }, []);

  // ── Sidebar Toggle ───────────────────────────
  const toggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => !prev);
  }, []);

  // ── Fetch Health Status ──────────────────────
  const fetchHealth = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      const data = await res.json();
      // data = { status: "ok", db_connected: true, llm_connected: false }
      const connected = data.status === 'ok' && data.db_connected;
      setHealthStatus(connected ? 'connected' : 'offline');
    } catch {
      setHealthStatus('offline');
    }
  }, []);

  // ── Fetch Schema ─────────────────────────────
  const fetchSchema = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/schema`);
      const data = await res.json();
      // data = { tables: [{name, columns, ...}], relationships: [...] }
      setSchema(data.tables || []);
    } catch {
      setSchema([]);
    }
  }, []);

  // ── Send Query ───────────────────────────────
  const sendQuery = useCallback(async (question) => {
    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    // Add placeholder assistant message (loading)
    const assistantId = Date.now() + 1;
    const loadingMessage = {
      id: assistantId,
      role: 'assistant',
      content: null,
      isLoading: true,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();

      // Replace loading message with actual response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? {
                ...msg,
                content: data.plain_english,
                data: data, // full API response for ResponseCard
                isLoading: false,
              }
            : msg
        )
      );
    } catch (error) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? {
                ...msg,
                content:
                  'Something went wrong. Please check your connection and try again.',
                isLoading: false,
                isError: true,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ── Follow-up click handler ──────────────────
  const handleFollowUpClick = useCallback(
    (question) => {
      if (!isLoading) {
        sendQuery(question);
      }
    },
    [isLoading, sendQuery]
  );

  // ── Initial Data Fetch ───────────────────────
  useEffect(() => {
    const init = async () => {
      await Promise.allSettled([fetchHealth(), fetchSchema()]);
      setIsInitializing(false);
    };
    init();
  }, [fetchHealth, fetchSchema]);

  // ── Periodic Health Check (every 30s) ────────
  useEffect(() => {
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  // ── Render ───────────────────────────────────
  if (isInitializing) {
    return (
      <div className="app" data-theme={theme}>
        <div className="app-loading">
          <div className="app-loading-spinner" />
          <span className="app-loading-text">Initializing QueryMind…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="app" data-theme={theme}>
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={toggleSidebar}
        healthStatus={healthStatus}
      />

      <div className="app-body">
        {/* Mobile overlay when sidebar is open */}
        <div
          className={`sidebar-overlay ${sidebarOpen ? 'active' : ''}`}
          onClick={() => setSidebarOpen(false)}
        />

        <div className={`sidebar-wrapper ${sidebarOpen ? '' : 'collapsed'}`}>
          <Sidebar
            isOpen={sidebarOpen}
            schema={schema}
            messages={messages}
            onSelectQuery={handleFollowUpClick}
            activeTab={sidebarTab}
            onTabChange={setSidebarTab}
          />
        </div>

        <main className="main-content">
          <ChatInterface
            messages={messages}
            onSendMessage={sendQuery}
            isLoading={isLoading}
            onFollowUpClick={handleFollowUpClick}
          />
        </main>
      </div>
    </div>
  );
}

export default App;
