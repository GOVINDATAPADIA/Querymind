import { useState, useEffect, useRef } from 'react';
import { ChevronDown, Clock, Rows3, Code, Copy, Check } from 'lucide-react';
import hljs from 'highlight.js/lib/core';
import sql from 'highlight.js/lib/languages/sql';
import DataTable from '../DataTable/DataTable';
import ChartRenderer from '../ChartRenderer/ChartRenderer';
import './ResponseCard.css';

// Register SQL language for highlight.js
hljs.registerLanguage('sql', sql);

function CollapsibleSection({ title, icon, defaultOpen = false, children }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="response-section">
      <button
        className="response-section-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        {icon}
        <span>{title}</span>
        <ChevronDown
          size={14}
          className={`response-section-chevron ${isOpen ? 'response-section-chevron--open' : ''}`}
        />
      </button>
      {isOpen && <div className="response-section-body">{children}</div>}
    </div>
  );
}

function SqlViewer({ sql: sqlCode }) {
  const [copied, setCopied] = useState(false);
  const codeRef = useRef(null);

  useEffect(() => {
    if (codeRef.current) {
      // Remove previous highlighting
      codeRef.current.removeAttribute('data-highlighted');
      hljs.highlightElement(codeRef.current);
    }
  }, [sqlCode]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sqlCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback copy
      const textarea = document.createElement('textarea');
      textarea.value = sqlCode;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="sql-viewer">
      <div className="sql-code-block">
        <button
          className={`sql-copy-btn ${copied ? 'sql-copy-btn--copied' : ''}`}
          onClick={handleCopy}
          title="Copy SQL"
        >
          {copied ? <Check size={12} /> : <Copy size={12} />}
          {copied ? 'Copied' : 'Copy'}
        </button>
        <pre>
          <code ref={codeRef} className="language-sql">
            {sqlCode}
          </code>
        </pre>
      </div>
    </div>
  );
}

export default function ResponseCard({ data, onFollowUpClick }) {
  if (!data) return null;

  const {
    plain_english,
    sql_generated,
    result_table,
    chart_suggestion,
    follow_up_suggestions,
    execution_time_ms,
  } = data;

  const rowCount = result_table ? result_table.length : 0;

  return (
    <div className="response-card">
      {/* Plain English Answer */}
      {plain_english && (
        <div className="response-answer">{plain_english}</div>
      )}

      {/* Execution Stats */}
      <div className="response-stats">
        {execution_time_ms != null && (
          <span className="response-stat">
            <Clock size={12} className="response-stat-icon" />
            {execution_time_ms}ms
          </span>
        )}
        <span className="response-stat">
          <Rows3 size={12} className="response-stat-icon" />
          {rowCount} row{rowCount !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Data Table (collapsible) */}
      {result_table && result_table.length > 0 && (
        <CollapsibleSection title="Data" defaultOpen={true}>
          <DataTable data={result_table} />
        </CollapsibleSection>
      )}

      {/* Chart (collapsible) */}
      {chart_suggestion &&
        chart_suggestion.type &&
        chart_suggestion.type !== 'table' && (
          <CollapsibleSection title="Visualization" defaultOpen={true}>
            <ChartRenderer chartSuggestion={chart_suggestion} />
          </CollapsibleSection>
        )}

      {/* SQL Viewer (collapsible) */}
      {sql_generated && (
        <CollapsibleSection
          title="SQL Query"
          icon={<Code size={14} />}
          defaultOpen={false}
        >
          <SqlViewer sql={sql_generated} />
        </CollapsibleSection>
      )}

      {/* Follow-up Pills */}
      {follow_up_suggestions && follow_up_suggestions.length > 0 && (
        <div className="followup-pills">
          {follow_up_suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              className="followup-pill"
              onClick={() => onFollowUpClick && onFollowUpClick(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
