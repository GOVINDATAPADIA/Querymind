import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Database, Sparkles } from 'lucide-react';
import ResponseCard from '../ResponseCard/ResponseCard';
import './ChatInterface.css';

const EXAMPLE_QUESTIONS = [
  'Show me the top 10 customers by revenue',
  'What were total sales last month?',
  'List all products with low inventory',
  'Compare revenue across regions',
  'Show the average order value by category',
];

function TypingIndicator() {
  return (
    <div className="chat-message chat-message--assistant">
      <div className="chat-message-bubble">
        <div className="typing-indicator">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
      </div>
    </div>
  );
}

function WelcomeScreen({ onChipClick }) {
  return (
    <div className="chat-welcome">
      <Database size={48} className="chat-welcome-icon" />
      <div className="chat-welcome-title">Welcome to QueryMind</div>
      <p className="chat-welcome-subtitle">
        Ask questions about your database in plain English. I'll generate SQL,
        run it, and present the results with charts and insights.
      </p>
      <div className="chat-welcome-chips">
        {EXAMPLE_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            className="chat-welcome-chip"
            onClick={() => onChipClick(q)}
          >
            <Sparkles size={13} style={{ marginRight: 6, verticalAlign: -2 }} />
            {q}
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
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  const autoResize = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 84) + 'px';
    }
  }, []);

  useEffect(() => {
    autoResize();
  }, [input, autoResize]);

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

  const hasMessages = messages && messages.length > 0;

  return (
    <div className="chat-interface">
      {/* Message area / Welcome */}
      {hasMessages ? (
        <div className="chat-messages">
          {messages.map((msg) => {
            // Skip rendering loading messages — we show TypingIndicator instead
            if (msg.isLoading) return null;

            return (
              <div
                key={msg.id}
                className={`chat-message chat-message--${msg.role}`}
              >
                <div className="chat-message-bubble">
                  {msg.role === 'user' ? (
                    msg.content
                  ) : msg.isError ? (
                    <div className="chat-error">{msg.content}</div>
                  ) : (
                    <ResponseCard
                      data={msg.data}
                      onFollowUpClick={onFollowUpClick}
                    />
                  )}
                </div>
              </div>
            );
          })}

          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      ) : (
        <WelcomeScreen onChipClick={handleChipClick} />
      )}

      {/* Input area */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            className="chat-textarea"
            placeholder="Ask a question about your data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
          />
          <button
            className="chat-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            title="Send message"
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
