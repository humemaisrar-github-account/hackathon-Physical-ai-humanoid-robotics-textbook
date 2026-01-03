import React, { useState } from 'react';
import './RagChatbot.css';

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface ChatInterfaceProps {
  onSendMessage: (message: string, mode: string, selectedText?: string) => void;
  messages: ChatMessage[];
  isLoading: boolean;
  selectedText?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onSendMessage,
  messages,
  isLoading,
  selectedText
}) => {
  const [inputValue, setInputValue] = useState('');
  const [mode, setMode] = useState<'book-wide' | 'selected-text-only'>('book-wide');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue, mode, mode === 'selected-text-only' ? selectedText : undefined);
      setInputValue('');
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>AI Textbook Assistant</h3>
        <div className="mode-selector">
          <label>
            <input
              type="radio"
              value="book-wide"
              checked={mode === 'book-wide'}
              onChange={() => setMode('book-wide')}
            />
            Entire Book
          </label>
          <label>
            <input
              type="radio"
              value="selected-text-only"
              checked={mode === 'selected-text-only'}
              onChange={() => setMode('selected-text-only')}
            />
            Selected Text Only
          </label>
        </div>
        {mode === 'selected-text-only' && selectedText && (
          <div className="selected-text-preview">
            <strong>Selected Text:</strong> {selectedText.substring(0, 100)}...
          </div>
        )}
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender}-message`}
          >
            <div className="message-content">{message.text}</div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-content loading">AI is thinking...</div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={`Ask a question... (${mode === 'book-wide' ? 'Entire book' : 'Selected text only'})`}
          className="chat-input"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || !inputValue.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;