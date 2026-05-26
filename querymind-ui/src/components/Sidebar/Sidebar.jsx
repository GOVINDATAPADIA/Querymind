import { useState } from 'react';
import {
  ChevronRight,
  Table2,
  MessageSquare,
  DatabaseZap,
} from 'lucide-react';
import './Sidebar.css';

/* ---- Schema Explorer ---- */
function SchemaExplorer({ schema }) {
  const [expanded, setExpanded] = useState({});

  if (!schema || schema.length === 0) {
    return (
      <div className="schema-empty">
        <DatabaseZap size={28} />
        <span>No schema loaded</span>
      </div>
    );
  }

  const toggle = (name) =>
    setExpanded((prev) => ({ ...prev, [name]: !prev[name] }));

  return (
    <div>
      {schema.map((table) => (
        <div className="schema-table-card" key={table.name}>
          <button
            className="schema-table-header"
            onClick={() => toggle(table.name)}
          >
            <Table2 size={14} className="schema-table-icon" />
            <span className="schema-table-name">{table.name}</span>
            <ChevronRight
              size={14}
              className={`schema-chevron ${expanded[table.name] ? 'schema-chevron--open' : ''}`}
            />
          </button>

          {expanded[table.name] && (
            <div className="schema-columns">
              {table.columns.map((col) => (
                <div className="schema-column" key={col.name}>
                  <span className="schema-column-name">{col.name}</span>
                  <span className="schema-column-type">{col.type}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/* ---- History list ---- */
function HistoryList({ messages, onSelectQuery }) {
  // Extract user messages as history items
  const userMessages = messages
    ? messages.filter((m) => m.role === 'user')
    : [];

  if (userMessages.length === 0) {
    return (
      <div className="history-empty">
        <MessageSquare size={28} />
        <span>No queries yet</span>
      </div>
    );
  }

  return (
    <div>
      {userMessages.map((msg, idx) => (
        <div
          className="history-item"
          key={idx}
          onClick={() => onSelectQuery && onSelectQuery(msg.content)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              onSelectQuery && onSelectQuery(msg.content);
            }
          }}
        >
          <span className="history-item-text">{msg.content}</span>
          <span className="history-item-time">
            {msg.timestamp
              ? new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })
              : ''}
          </span>
        </div>
      ))}
    </div>
  );
}

/* ---- Sidebar ---- */
export default function Sidebar({
  isOpen,
  schema,
  messages,
  onSelectQuery,
  activeTab,
  onTabChange,
}) {
  return (
    <>
      <div
        className={`sidebar-overlay ${isOpen ? 'sidebar-overlay--visible' : ''}`}
        onClick={() => onTabChange && onTabChange(activeTab)}
      />
      <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`}>
        {/* Tabs */}
        <div className="sidebar-tabs">
          <button
            className={`sidebar-tab ${activeTab === 'history' ? 'sidebar-tab--active' : ''}`}
            onClick={() => onTabChange && onTabChange('history')}
          >
            History
          </button>
          <button
            className={`sidebar-tab ${activeTab === 'schema' ? 'sidebar-tab--active' : ''}`}
            onClick={() => onTabChange && onTabChange('schema')}
          >
            Schema
          </button>
        </div>

        {/* Content */}
        <div className="sidebar-content">
          {activeTab === 'history' ? (
            <HistoryList messages={messages} onSelectQuery={onSelectQuery} />
          ) : (
            <SchemaExplorer schema={schema} />
          )}
        </div>
      </aside>
    </>
  );
}
