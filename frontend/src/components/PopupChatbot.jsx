import React, { useState, useEffect, useRef } from 'react';
import './PopupChatbot.css';

const PopupChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [hasBeenOpened, setHasBeenOpened] = useState(false);
  const messagesEndRef = useRef(null);

  const API_BASE_URL = 'http://localhost:8003';

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
        text: 'Sorry, there was an error processing your request. Please check that the backend is running.',
        sender: 'bot',
        isError: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpen = () => {
    setIsOpen(true);
    setHasBeenOpened(true);
    if (messages.length === 0) {
      // Add welcome message when first opened
      setMessages([{
        id: Date.now(),
        text: 'Hello! How can I help you today?',
        sender: 'bot',
        timestamp: new Date()
      }]);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  const handleMinimize = () => {
    setIsOpen(false);
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

  return (
    <div className="popup-chatbot">
      {!isOpen && (
        <button className="chatbot-icon" onClick={handleOpen} title="Open chat">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H16.58L15.5 19.45C15.3433 19.8029 15.0721 20.0971 14.727 20.2858C14.3819 20.4745 13.981 20.5462 13.585 20.488C13.2367 20.4368 12.908 20.303 12.626 20.099C12.344 19.895 12.117 19.627 11.964 19.318L11.464 18.318C11.311 18.009 11.084 17.741 10.802 17.537C10.52 17.333 10.191 17.2 9.843 17.149L7 16.5C6.46967 16.5 5.96086 16.2893 5.58579 15.9142C5.21071 15.5391 5 15.0304 5 14.5V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V15Z" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M9 10H15" stroke="#ffffff" strokeWidth="2" strokeLinecap="round"/>
            <path d="M9 14H13" stroke="#ffffff" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      )}

      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <span className="chatbot-title">Assistant</span>
            <div className="chatbot-controls">
              <button className="minimize-btn" onClick={handleMinimize} title="Minimize">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 8H13" stroke="#ffffff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
              <button className="close-btn" onClick={handleClose} title="Close">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 4L4 12M4 4L12 12" stroke="#ffffff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <div className="chatbot-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-content">
                  <p>{message.text}</p>
                  {message.sources && message.sources.length > 0 && (
                    <div className="sources">
                      <details>
                        <summary>Sources ({message.sources.length})</summary>
                        <ul>
                          {message.sources.map((source, index) => (
                            <li key={index}>
                              <div className="source-title">{source.title || 'Source'}</div>
                              <div className="source-content">{source.content.substring(0, 100)}{source.content.length > 100 ? '...' : ''}</div>
                              {source.url && <a href={source.url} target="_blank" rel="noopener noreferrer">View Source</a>}
                            </li>
                          ))}
                        </ul>
                      </details>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message bot">
                <div className="message-content">
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

          <form onSubmit={handleSubmit} className="chatbot-input-form">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 1L8.5 15L7 9.5L1 7L15 1Z" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </form>

          {selectedText && (
            <div className="selected-text-preview">
              <small>Selected: {selectedText.substring(0, 50)}...</small>
              <button onClick={handleTextSelection} className="use-selected-btn">Use</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PopupChatbot;