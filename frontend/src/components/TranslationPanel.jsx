import React, { useState } from 'react';
import './RagChatbot.css';

const TranslationPanel = ({
  user,
  onTranslation,
  currentContent,
  currentChapterId
}) => {
  const [targetLanguage, setTargetLanguage] = useState('ur');
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState('');
  const [translatedContent, setTranslatedContent] = useState(null);

  const languages = [
    { code: 'ur', name: 'Urdu' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ru', name: 'Russian' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'ar', name: 'Arabic' }
  ];

  const handleTranslate = async () => {
    if (!user) {
      setError('Please log in to use translation features');
      return;
    }

    if (!currentContent) {
      setError('No content to translate');
      return;
    }

    try {
      setIsTranslating(true);
      setError('');
      setTranslatedContent(null);

      // In a real implementation, this would call the backend API
      // const translationResult = await apiClient.translateContent(
      //   currentContent,
      //   targetLanguage
      // );

      // For now, simulate the translation process
      setTimeout(() => {
        setTranslatedContent(`[Translated content in ${languages.find(lang => lang.code === targetLanguage)?.name} would appear here]`);
        setIsTranslating(false);

        if (onTranslation) {
          onTranslation({
            originalContent: currentContent,
            translatedContent: `[Translated content in ${languages.find(lang => lang.code === targetLanguage)?.name}]`,
            targetLanguage,
            sourceLanguage: 'en'
          });
        }
      }, 1000);

    } catch (err) {
      setError('Failed to translate content');
      setIsTranslating(false);
    }
  };

  const handleTranslateChapter = async () => {
    if (!user) {
      setError('Please log in to use translation features');
      return;
    }

    if (!currentChapterId) {
      setError('No chapter selected for translation');
      return;
    }

    try {
      setIsTranslating(true);
      setError('');
      setTranslatedContent(null);

      // In a real implementation, this would call the backend API to translate a whole chapter
      // const translationResult = await apiClient.translateChapter(
      //   currentChapterId,
      //   targetLanguage
      // );

      // For now, simulate the translation process
      setTimeout(() => {
        setTranslatedContent(`[Translated chapter ${currentChapterId} in ${languages.find(lang => lang.code === targetLanguage)?.name} would appear here]`);
        setIsTranslating(false);

        if (onTranslation) {
          onTranslation({
            originalContent: `[Original chapter ${currentChapterId}]`,
            translatedContent: `[Translated chapter ${currentChapterId} in ${languages.find(lang => lang.code === targetLanguage)?.name}]`,
            targetLanguage,
            sourceLanguage: 'en',
            chapterId: currentChapterId
          });
        }
      }, 1500);

    } catch (err) {
      setError('Failed to translate chapter');
      setIsTranslating(false);
    }
  };

  const handleLanguageChange = (e) => {
    setTargetLanguage(e.target.value);
    setTranslatedContent(null); // Reset translated content when language changes
  };

  if (!user) {
    return (
      <div className="translation-panel">
        <div className="translation-message">
          <p>Please log in to access translation features.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="translation-panel">
      <h3>Translation</h3>

      {error && <div className="error-message">{error}</div>}

      <div className="translation-controls">
        <div className="form-group">
          <label htmlFor="targetLanguage">Target Language:</label>
          <select
            id="targetLanguage"
            value={targetLanguage}
            onChange={handleLanguageChange}
            disabled={isTranslating}
          >
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>

        <div className="translation-actions">
          <button
            onClick={handleTranslate}
            disabled={isTranslating || !currentContent}
            className="translate-button"
          >
            {isTranslating ? 'Translating...' : 'Translate Content'}
          </button>

          <button
            onClick={handleTranslateChapter}
            disabled={isTranslating || !currentChapterId}
            className="translate-chapter-button"
          >
            {isTranslating ? 'Translating...' : 'Translate Chapter'}
          </button>
        </div>
      </div>

      {translatedContent && (
        <div className="translation-result">
          <h4>Translation Result:</h4>
          <div className="translated-content">
            {translatedContent}
          </div>
        </div>
      )}
    </div>
  );
};

export default TranslationPanel;