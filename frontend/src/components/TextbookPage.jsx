import React, { useState, useEffect } from 'react';
import RagChatbot from './RagChatbot';
import './TextbookPage.css';

const TextbookPage = ({ chapterId, content }) => {
  const [showChatbot, setShowChatbot] = useState(false);
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [personalizedContent, setPersonalizedContent] = useState(null);
  const [translatedContent, setTranslatedContent] = useState(null);
  const [isUrdu, setIsUrdu] = useState(false);

  // Toggle chatbot visibility
  const toggleChatbot = () => {
    setShowChatbot(!showChatbot);
  };

  // Handle personalization
  const handlePersonalize = async () => {
    try {
      // In a real implementation, this would call the personalization API
      // For now, we'll just simulate personalization
      setIsPersonalized(true);
      setPersonalizedContent(content + " [This content has been personalized based on your background]");
    } catch (error) {
      console.error('Error personalizing content:', error);
    }
  };

  // Handle translation to Urdu
  const handleTranslateToUrdu = async () => {
    try {
      // In a real implementation, this would call the translation API
      // For now, we'll just simulate translation with placeholder text
      const simulatedUrdu = "یہ متن یو اردو میں ترجمہ کیا گیا ہے۔ یہ اصل مواد کا ترجمہ ہے جو کہ کتاب میں موجود تھا۔";
      setTranslatedContent(simulatedUrdu);
      setIsUrdu(true);
    } catch (error) {
      console.error('Error translating to Urdu:', error);
    }
  };

  // Reset to original content
  const handleResetContent = () => {
    setIsPersonalized(false);
    setPersonalizedContent(null);
    setTranslatedContent(null);
    setIsUrdu(false);
  };

  // Get the content to display
  const displayContent = isUrdu
    ? translatedContent
    : isPersonalized
      ? personalizedContent
      : content;

  return (
    <div className="textbook-page">
      <header className="page-header">
        <h1>AI-Native Textbook</h1>
        <div className="page-controls">
          <button onClick={handlePersonalize} className="control-btn">
            Personalize Chapter
          </button>
          <button onClick={handleTranslateToUrdu} className="control-btn">
            Translate to Urdu
          </button>
          <button onClick={handleResetContent} className="control-btn">
            Reset
          </button>
          <button
            onClick={toggleChatbot}
            className={`control-btn ${showChatbot ? 'active' : ''}`}
          >
            {showChatbot ? 'Hide Assistant' : 'Show Assistant'}
          </button>
        </div>
      </header>

      <main className="page-content">
        {isUrdu && (
          <div className="urdu-notice">
            <p>Displaying content in Urdu</p>
          </div>
        )}
        <div className={`content-display ${isUrdu ? 'urdu-content' : ''}`}>
          {displayContent || (
            <div className="default-content">
              <h2>Chapter: {chapterId || 'Introduction'}</h2>
              <p>This is where the textbook content would be displayed. Select text to ask questions or use the assistant.</p>
              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
              <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
              <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
            </div>
          )}
        </div>
      </main>

      {showChatbot && (
        <div className="chatbot-panel">
          <RagChatbot chapterId={chapterId} />
        </div>
      )}
    </div>
  );
};

export default TextbookPage;