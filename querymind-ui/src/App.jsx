import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header/Header';
import Sidebar from './components/Sidebar/Sidebar';
import ChatInterface from './components/ChatInterface/ChatInterface';
import UploadModal from './components/UploadModal/UploadModal';
import './App.css';

const API_BASE = 'https://query-backend.up.railway.app';

export default function App() {
  // ── State ────────────────────────────────────
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('querymind-theme') || 'dark';
  });
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarTab, setSidebarTab] = useState('schema');
  const [messages, setMessages] = useState([]);
  const [schema, setSchema] = useState([]);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

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
      const connected = data.status === 'ok' && data.db_connected;
      setHealthStatus(connected ? 'connected' : 'offline');
    } catch {
      setHealthStatus('offline');
    }
  }, []);

  // ── Fetch Schema & Suggested Questions ───────
  const fetchSchemaAndQuestions = useCallback(async () => {
    try {
      // 1. Fetch Schema
      const schemaRes = await fetch(`${API_BASE}/schema`);
      const schemaData = await schemaRes.json();
      if (schemaData.tables && Array.isArray(schemaData.tables)) {
        setSchema(schemaData.tables);
      } else if (Array.isArray(schemaData)) {
        setSchema(schemaData);
      } else if (typeof schemaData === 'object') {
        setSchema(schemaData);
      } else {
        setSchema([]);
      }
    } catch {
      setSchema([]);
    }

    try {
      // 2. Fetch AI-Suggested Questions for Welcome Screen
      const qRes = await fetch(`${API_BASE}/suggested-questions`);
      const qData = await qRes.json();
      if (qData.questions && Array.isArray(qData.questions)) {
        setSuggestedQuestions(qData.questions);
      }
    } catch {
      // Keep defaults
    }
  }, []);

  // ── Dataset Upload Success Handler ───────────
  const handleUploadSuccess = useCallback(
    async (uploadResult) => {
      // Refetch schema and dynamic questions immediately
      await fetchSchemaAndQuestions();

      // Post success notification in chat
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const systemMessage = {
        id: Date.now(),
        type: 'assistant',
        role: 'assistant',
        text: `✅ Successfully imported table **${uploadResult.table_name}** with ${uploadResult.row_count.toLocaleString()} rows and ${uploadResult.column_count} columns! You can now ask questions about this dataset in plain English.`,
        content: `✅ Successfully imported table **${uploadResult.table_name}** with ${uploadResult.row_count.toLocaleString()} rows and ${uploadResult.column_count} columns! You can now ask questions about this dataset in plain English.`,
        timestamp: timeStr,
      };

      setMessages((prev) => [...prev, systemMessage]);
    },
    [fetchSchemaAndQuestions]
  );

  // ── Send Query ───────────────────────────────
  const sendQuery = useCallback(async (question) => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      role: 'user',
      text: question,
      content: question,
      timestamp: timeStr,
    };

    // Add placeholder assistant message (loading)
    const assistantId = Date.now() + 1;
    const loadingMessage = {
      id: assistantId,
      type: 'assistant',
      role: 'assistant',
      text: null,
      content: null,
      isLoading: true,
      timestamp: timeStr,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: Failed to execute query`);
      }

      const data = await res.json();

      // Replace loading message with actual response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? {
                ...msg,
                type: 'assistant',
                role: 'assistant',
                text: data.plain_english,
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
                type: 'assistant',
                role: 'assistant',
                error:
                  error.message || 'Something went wrong. Please check your connection and try again.',
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

  // ── Clear Chat / History ─────────────────────
  const handleClearChat = useCallback(() => {
    setMessages([]);
  }, []);

  // ── Initial Data Fetch ───────────────────────
  useEffect(() => {
    const init = async () => {
      await Promise.allSettled([fetchHealth(), fetchSchemaAndQuestions()]);
      setIsInitializing(false);
    };
    init();
  }, [fetchHealth, fetchSchemaAndQuestions]);

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
            onRefreshSchema={fetchSchemaAndQuestions}
            onClearHistory={handleClearChat}
            onOpenUpload={() => setIsUploadOpen(true)}
          />
        </div>

        <main className="main-content">
          <ChatInterface
            messages={messages}
            onSendMessage={sendQuery}
            isLoading={isLoading}
            onFollowUpClick={handleFollowUpClick}
            onClearChat={handleClearChat}
            suggestedQuestions={suggestedQuestions}
            onOpenUpload={() => setIsUploadOpen(true)}
          />
        </main>
      </div>

      {/* Dataset Upload Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
        apiBase={API_BASE}
      />
    </div>
  );
}
