import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { LoadingIndicator } from './LoadingIndicator';

export default function ChatbotWidget() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');

  useEffect(() => {
    const handleMouseUp = () => {
      const selection = window.getSelection().toString();
      if (selection) {
        setSelectedText(selection);
      }
    };

    document.addEventListener('mouseup', handleMouseUp);

    // Fetch chat history
    const fetchHistory = async () => {
      try {
        const response = await fetch('/api/history/1'); // Placeholder for session ID
        if(response.ok) {
          const history = await response.json();
          setMessages(history);
        }
      } catch (error) {
        console.error('Error fetching chat history:', error);
      }
    };

    fetchHistory();

    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const handleSendMessage = async (text) => {
    const newMessage = { text, isUser: true };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: text, selected_text: selectedText }),
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
      setSelectedText('');
    }
  };

  return (
    <div className={styles.widgetContainer}>
      <div className={styles.messageContainer}>
        {messages.map((msg, index) => (
          <MessageBubble key={index} message={msg} isUser={msg.isUser} />
        ))}
        {isLoading && <LoadingIndicator />}
      </div>
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
}
