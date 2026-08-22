import { useState, useMemo } from 'react';
import {
  ChevronRight,
  ChevronDown,
  Table2,
  MessageSquare,
  DatabaseZap,
  Search,
  Key,
  Link2,
  Trash2,
  ChevronsUpDown,
  RotateCw,
  UploadCloud,
} from 'lucide-react';
import './Sidebar.css';

/* ---- Schema Explorer ---- */
function SchemaExplorer({ schema, onRefreshSchema, onOpenUpload }) {
  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState({});

  // Normalize schema to array of tables
  const tableList = useMemo(() => {
    if (!schema) return [];
    if (Array.isArray(schema)) return schema;
    if (schema.tables && Array.isArray(schema.tables)) return schema.tables;
    if (typeof schema === 'object') {
      return Object.entries(schema).map(([name, info]) => ({
        name,
        columns: info.columns || [],
        primary_keys: info.primary_keys || [],
        foreign_keys: info.foreign_keys || [],
      }));
    }
    return [];
  }, [schema]);

  // Filtered tables based on search
  const filteredTables = useMemo(() => {
    if (!search.trim()) return tableList;
    const query = search.toLowerCase();
    return tableList.filter(
      (table) =>
        table.name.toLowerCase().includes(query) ||
        (table.columns &&
          table.columns.some((col) => col.name.toLowerCase().includes(query)))
    );
  }, [tableList, search]);

  const toggle = (name) =>
    setExpanded((prev) => ({ ...prev, [name]: !prev[name] }));

  const expandAll = () => {
    const all = {};
    tableList.forEach((t) => (all[t.name] = true));
    setExpanded(all);
  };

  const collapseAll = () => setExpanded({});

  if (tableList.length === 0) {
    return (
      <div className="schema-empty">
        <DatabaseZap size={32} className="schema-empty-icon" />
        <span className="schema-empty-title">No schema loaded</span>
        <span className="schema-empty-desc">Upload your CSV dataset or refresh to inspect tables</span>
        
        {onOpenUpload && (
          <button className="schema-upload-primary-btn" onClick={onOpenUpload}>
            <UploadCloud size={14} /> Upload CSV / Excel
          </button>
        )}

        {onRefreshSchema && (
          <button className="schema-refresh-btn" onClick={onRefreshSchema}>
            <RotateCw size={13} /> Refresh Schema
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="schema-explorer">
      {onOpenUpload && (
        <div className="schema-upload-banner">
          <button className="schema-upload-btn" onClick={onOpenUpload}>
            <UploadCloud size={14} className="schema-upload-btn-icon" />
            <span>Upload CSV / Excel Dataset</span>
          </button>
        </div>
      )}

      <div className="schema-toolbar">
        <div className="schema-search-box">
          <Search size={14} className="schema-search-icon" />
          <input
            type="text"
            placeholder="Filter tables & columns..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="schema-search-input"
          />
          {search && (
            <button className="schema-search-clear" onClick={() => setSearch('')}>
              ×
            </button>
          )}
        </div>
        <div className="schema-actions">
          <button className="schema-action-btn" onClick={expandAll} title="Expand All">
            <ChevronsUpDown size={13} />
          </button>
          {onRefreshSchema && (
            <button className="schema-action-btn" onClick={onRefreshSchema} title="Refresh Schema">
              <RotateCw size={13} />
            </button>
          )}
        </div>
      </div>

      <div className="schema-tables-count">
        <span>{filteredTables.length} {filteredTables.length === 1 ? 'table' : 'tables'} available</span>
      </div>

      <div className="schema-list">
        {filteredTables.map((table) => {
          const isOpen = Boolean(expanded[table.name]);
          const pkSet = new Set(table.primary_keys || []);
          const fkMap = new Map((table.foreign_keys || []).map((fk) => [fk.column, fk]));

          return (
            <div className={`schema-table-card ${isOpen ? 'schema-table-card--open' : ''}`} key={table.name}>
              <button
                className="schema-table-header"
                onClick={() => toggle(table.name)}
              >
                <Table2 size={14} className="schema-table-icon" />
                <span className="schema-table-name">{table.name}</span>
                <span className="schema-col-count">{table.columns?.length || 0} cols</span>
                {isOpen ? (
                  <ChevronDown size={14} className="schema-chevron schema-chevron--open" />
                ) : (
                  <ChevronRight size={14} className="schema-chevron" />
                )}
              </button>

              {isOpen && table.columns && (
                <div className="schema-columns">
                  {table.columns.map((col) => {
                    const isPK = pkSet.has(col.name);
                    const fk = fkMap.get(col.name);

                    return (
                      <div className="schema-column" key={col.name}>
                        <div className="schema-column-left">
                          {isPK && <Key size={11} className="schema-pk-icon" title="Primary Key" />}
                          {fk && <Link2 size={11} className="schema-fk-icon" title={`References ${fk.references_table}.${fk.references_column}`} />}
                          <span className={`schema-column-name ${isPK ? 'schema-column-name--pk' : ''}`}>
                            {col.name}
                          </span>
                        </div>
                        <span className="schema-column-type">{col.type || 'TEXT'}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ---- History List ---- */
function HistoryList({ messages, onSelectQuery, onClearHistory }) {
  const historyItems = useMemo(() => {
    return messages
      .filter((m) => m.type === 'user')
      .map((m) => ({
        id: m.id,
        text: m.text,
        timestamp: m.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }))
      .reverse();
  }, [messages]);

  if (historyItems.length === 0) {
    return (
      <div className="history-empty">
        <MessageSquare size={32} className="history-empty-icon" />
        <span className="history-empty-title">No query history yet</span>
        <span className="history-empty-desc">Your past questions in this session will appear here</span>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-toolbar">
        <span className="history-count">{historyItems.length} queries</span>
        {onClearHistory && (
          <button className="history-clear-btn" onClick={onClearHistory} title="Clear Session History">
            <Trash2 size={13} /> Clear
          </button>
        )}
      </div>
      <div className="history-list">
        {historyItems.map((item) => (
          <div
            key={item.id}
            className="history-item"
            onClick={() => onSelectQuery && onSelectQuery(item.text)}
          >
            <div className="history-item-header">
              <span className="history-item-text">{item.text}</span>
            </div>
            <span className="history-item-time">{item.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---- Main Sidebar Component ---- */
export default function Sidebar({
  isOpen,
  schema,
  messages,
  onSelectQuery,
  activeTab = 'schema',
  onTabChange,
  onRefreshSchema,
  onClearHistory,
  onOpenUpload,
}) {
  return (
    <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`}>
      <div className="sidebar-tabs">
        <button
          className={`sidebar-tab ${activeTab === 'schema' ? 'sidebar-tab--active' : ''}`}
          onClick={() => onTabChange('schema')}
        >
          <Table2 size={14} style={{ marginRight: 6, verticalAlign: -2 }} />
          Schema
        </button>
        <button
          className={`sidebar-tab ${activeTab === 'history' ? 'sidebar-tab--active' : ''}`}
          onClick={() => onTabChange('history')}
        >
          <MessageSquare size={14} style={{ marginRight: 6, verticalAlign: -2 }} />
          History
        </button>
      </div>

      <div className="sidebar-content">
        {activeTab === 'schema' ? (
          <SchemaExplorer
            schema={schema}
            onRefreshSchema={onRefreshSchema}
            onOpenUpload={onOpenUpload}
          />
        ) : (
          <HistoryList
            messages={messages}
            onSelectQuery={onSelectQuery}
            onClearHistory={onClearHistory}
          />
        )}
      </div>
    </aside>
  );
}
