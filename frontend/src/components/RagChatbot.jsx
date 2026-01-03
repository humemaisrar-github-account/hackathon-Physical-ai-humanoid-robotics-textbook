import React, { useState, useEffect, useRef } from 'react';
import './RagChatbot.css';

const RagChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const API_BASE_URL = 'http://localhost:8000';

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Add event listener for text selection
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection().toString().trim();
      if (selection && selection.length > 10) { // Only set if substantial text is selected
        setSelectedText(selection);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue,
          selected_text: selectedText || null,
          top_k: 3,
          include_sources: true
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        sources: data.sources,
        timing: data.timing,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
      setSelectedText(''); // Clear selected text after successful submission
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: `Sorry, there was an error processing your request: ${error.message}. Please check that the backend is running at ${API_BASE_URL}.`,
        sender: 'bot',
        isError: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextSelection = () => {
    const selection = window.getSelection().toString().trim();
    if (selection) {
      setSelectedText(selection);
      if (inputValue) {
        setInputValue(`Based on: "${selection}". ${inputValue}`);
      } else {
        setInputValue(`Based on: "${selection}". `);
      }
    }
  };

  const clearChat = () => {
    setMessages([]);
    setInputValue('');
    setSelectedText('');
    setError('');
  };

  return (
    <div className="rag-chatbot">
      <div className="chat-header">
        <h3>📚 RAG Chatbot</h3>
        <p>Ask questions about the book content</p>
      </div>

      <div className="chat-controls">
        <button onClick={handleTextSelection} className="select-text-btn" title="Use selected text from page">
          📝 Use Selected Text
        </button>
        <button onClick={clearChat} className="clear-chat-btn" title="Clear chat history">
          🗑️ Clear Chat
        </button>
      </div>

      {selectedText && (
        <div className="selected-text-preview">
          <small><strong>Selected text:</strong> "{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}"</small>
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h4>Welcome to the RAG Chatbot! 🤖</h4>
            <p>Ask me questions about the book content and I'll provide grounded responses with source citations.</p>
            <p>You can also select text on the page and click "Use Selected Text" to ask questions about specific content.</p>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-content">
              <div className="message-header">
                <span className="sender-name">{message.sender === 'user' ? 'You' : 'Assistant'}</span>
                <span className="timestamp">{message.timestamp?.toLocaleTimeString()}</span>
              </div>
              <p>{message.text}</p>

              {message.sources && message.sources.length > 0 && (
                <div className="sources">
                  <h5>📚 Sources:</h5>
                  {message.sources.map((source, index) => (
                    <div key={index} className="source">
                      <p><strong>{source.title || 'Source'}:</strong> {source.content.substring(0, 150)}{source.content.length > 150 ? '...' : ''}</p>
                      {source.url && (
                        <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-link">
                          🔗 View Source
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {message.timing && (
                <div className="timing-info">
                  <small>
                    Retrieval: {(message.timing.retrieval_time || 0).toFixed(3)}s,
                    Agent: {(message.timing.agent_time || 0).toFixed(3)}s,
                    Total: {(message.timing.total_time || 0).toFixed(3)}s
                  </small>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message bot">
            <div className="message-content">
              <div className="message-header">
                <span className="sender-name">Assistant</span>
              </div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="input-container">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask a question about the book content..."
            disabled={isLoading}
            className={error ? 'error' : ''}
          />
          <button type="submit" disabled={isLoading} className="send-btn">
            {isLoading ? 'Sending...' : '➤'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RagChatbot;