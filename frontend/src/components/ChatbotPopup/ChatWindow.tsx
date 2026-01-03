import React, { useState } from 'react';
import styles from './styles.module.css';

interface Message {
  text: string;
  isUser: boolean;
}

interface ChatWindowProps {
  onClose: () => void;
  onSendMessage: (message: string) => void;
  messages: Message[];
  isLoading: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ onClose, onSendMessage, messages, isLoading }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <div className={styles.popupContainer}>
      <div className={styles.header}>
        🤖 AI Assistant
        <button className={styles.closeButton} onClick={onClose}>×</button>
      </div>
      <div className={styles.messageArea}>
        {messages.map((message, index) => (
          <div key={index} className={`${styles.messageBubble} ${message.isUser ? styles.userBubble : styles.botBubble}`}>
            {message.text}
          </div>
        ))}
        {isLoading && <div className={styles.loadingIndicator}>Loading...</div>}
      </div>
      <form onSubmit={handleSubmit} className={styles.inputArea}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message..."
          className={styles.messageInput}
        />
        <button type="submit" className={styles.sendButton}>Send</button>
      </form>
    </div>
  );
};