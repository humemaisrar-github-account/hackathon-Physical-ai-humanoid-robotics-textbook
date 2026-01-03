import React, { useState } from 'react';
import styles from './styles.module.css';

export function MessageInput({ onSendMessage }) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.messageInputForm}>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Ask a question..."
        className={styles.messageInput}
      />
      <button type="submit" className={styles.sendButton}>Send</button>
    </form>
  );
}
