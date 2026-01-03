import React, { useState } from 'react';
import styles from './styles.module.css';
import { ToggleButton } from './ToggleButton';
import { ChatWindow } from './ChatWindow';

export default function ChatbotPopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{ text: "Hello 👋 How can I help you?", isUser: false }]);
  const [isLoading, setIsLoading] = useState(false);

  const handleToggleClick = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async (text: string) => {
    const newMessage = { text, isUser: true };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text, selected_text: null }), // Updated to UserMessage model
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      const botMessage = { text: data.answer, isUser: false };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error fetching data:', error);
      const errorMessage = { text: 'Sorry, something went wrong.', isUser: false };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatbotWrapper}>
      {isOpen && (
        <ChatWindow
          onClose={() => setIsOpen(false)}
          onSendMessage={handleSendMessage}
          messages={messages}
          isLoading={isLoading}
        />
      )}
      <ToggleButton isOpen={isOpen} onClick={handleToggleClick} />
    </div>
  );
}