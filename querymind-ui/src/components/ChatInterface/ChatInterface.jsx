import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Database, Sparkles, CornerDownLeft, Trash2, Bot } from 'lucide-react';
import ResponseCard from '../ResponseCard/ResponseCard';
import './ChatInterface.css';

const EXAMPLE_QUESTIONS = [
  { text: 'Show me the top 5 customers by total spend', category: 'Customers' },
  { text: 'Compare revenue across product categories', category: 'Revenue' },
  { text: 'What were total sales last month by region?', category: 'Sales' },
  { text: 'List products with low inventory under 20 units', category: 'Inventory' },
  { text: 'What is the average order value across regions?', category: 'Analytics' },
];

function TypingIndicator() {
  return (
    <div className="chat-message chat-message--assistant">
      <div className="chat-message-bubble">
        <div className="typing-indicator">
          <Bot size={16} className="typing-bot-icon" />
          <span>Generating query and analyzing data</span>
          <div className="typing-dots">
            <div className="typing-dot" />
            <div className="typing-dot" />
            <div className="typing-dot" />
          </div>
        </div>
      </div>
    </div>
  );
}

function WelcomeScreen({ onChipClick }) {
  return (
    <div className="chat-welcome">
      <div className="chat-welcome-icon-wrapper">
        <Database size={48} className="chat-welcome-icon" />
      </div>
      <div className="chat-welcome-title">Welcome to QueryMind</div>
      <p className="chat-welcome-subtitle">
        Ask questions about your database in plain English. I will generate SQL,
        execute it securely, and return data tables, charts, and business insights.
      </p>
      <div className="chat-welcome-chips">
        {EXAMPLE_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            className="chat-welcome-chip"
            onClick={() => onChipClick(q.text)}
          >
            <Sparkles size={12} className="chat-welcome-chip-icon" />
            <span className="chat-welcome-chip-text">{q.text}</span>
            <span className="chat-welcome-chip-tag">{q.category}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function ChatInterface({
  messages,
  onSendMessage,
  isLoading,
  onFollowUpClick,
  onClearChat,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to bottom on new messages
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  // Auto-resize textarea
  const handleInputChange = (e) => {
    setInput(e.target.value);
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSendMessage(trimmed);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChipClick = (question) => {
    if (isLoading) return;
    onSendMessage(question);
  };

  return (
    <div className="chat-interface">
      {messages.length > 0 && onClearChat && (
        <div className="chat-header-actions">
          <button className="chat-clear-btn" onClick={onClearChat} title="Clear conversation">
            <Trash2 size={13} /> Clear Chat
          </button>
        </div>
      )}

      {/* Messages area */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <WelcomeScreen onChipClick={handleChipClick} />
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`chat-message chat-message--${msg.type}`}
            >
              <div className="chat-message-bubble">
                {msg.type === 'user' ? (
                  <div className="chat-user-text">{msg.text}</div>
                ) : msg.error ? (
                  <div className="chat-error">{msg.error}</div>
                ) : (
                  <ResponseCard
                    data={msg.data}
                    onFollowUpClick={onFollowUpClick}
                  />
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            className="chat-textarea"
            placeholder="Ask a question about your database (e.g., 'What were top products by profit?')..."
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isLoading}
          />
          <button
            className="chat-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            title="Run Query (Enter ↵)"
            aria-label="Send message"
          >
            <span className="chat-send-btn-label">Run Query</span>
            <CornerDownLeft size={14} className="chat-send-btn-icon" />
          </button>
        </div>
        <div className="chat-input-hint">
          <span>Press <strong>Enter ↵</strong> to run query, <strong>Shift + Enter</strong> for a new line</span>
        </div>
      </div>
    </div>
  );
}
