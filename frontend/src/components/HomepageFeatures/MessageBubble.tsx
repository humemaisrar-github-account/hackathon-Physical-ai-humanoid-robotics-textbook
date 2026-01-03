import React from 'react';
import styles from './styles.module.css';

export function MessageBubble({ message, isUser }) {
  const bubbleClass = isUser ? styles.userBubble : styles.botBubble;
  return (
    <div className={`${styles.messageBubble} ${bubbleClass}`}>
      {message.text}
    </div>
  );
}
