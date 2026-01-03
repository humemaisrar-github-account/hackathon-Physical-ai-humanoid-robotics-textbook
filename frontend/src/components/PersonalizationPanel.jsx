import React, { useState, useEffect } from 'react';
import './RagChatbot.css';

const PersonalizationPanel = ({
  user,
  onPersonalizationUpdate,
  currentChapterId,
  onChapterPersonalize
}) => {
  const [personalizationSettings, setPersonalizationSettings] = useState({
    difficultyLevel: 'intermediate',
    learningStyle: 'examples_and_applications',
    backgroundMatching: true,
    preferredLanguage: 'en'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      fetchPersonalizationSettings();
    }
  }, [user]);

  const fetchPersonalizationSettings = async () => {
    if (!user) return;

    try {
      setIsLoading(true);
      // In a real implementation, this would fetch user's personalization settings
      // For now, we'll use the default settings
      setPersonalizationSettings({
        difficultyLevel: 'intermediate',
        learningStyle: 'examples_and_applications',
        backgroundMatching: true,
        preferredLanguage: 'en'
      });
    } catch (err) {
      setError('Failed to load personalization settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSettingChange = (setting, value) => {
    setPersonalizationSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  const handleSaveSettings = async () => {
    if (!user) {
      setError('Please log in to save personalization settings');
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      // In a real implementation, this would call the backend API
      // await apiClient.updatePersonalizationSettings(user.id, personalizationSettings);

      // Notify parent component of the update
      if (onPersonalizationUpdate) {
        onPersonalizationUpdate(personalizationSettings);
      }
    } catch (err) {
      setError('Failed to save personalization settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePersonalizeChapter = async () => {
    if (!user || !currentChapterId) {
      setError('User and chapter ID are required for personalization');
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      // In a real implementation, this would call the backend API to personalize the current chapter
      // const personalizedContent = await apiClient.personalizeChapter(currentChapterId, user.id, personalizationSettings);

      // Notify parent component
      if (onChapterPersonalize) {
        onChapterPersonalize(currentChapterId, personalizationSettings);
      }
    } catch (err) {
      setError('Failed to personalize chapter');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="personalization-panel">
        <div className="personalization-message">
          <p>Please log in to access personalization features.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="personalization-panel">
      <h3>Personalization Settings</h3>

      {error && <div className="error-message">{error}</div>}

      <div className="personalization-form">
        <div className="form-group">
          <label>Difficulty Level:</label>
          <select
            value={personalizationSettings.difficultyLevel}
            onChange={(e) => handleSettingChange('difficultyLevel', e.target.value)}
            disabled={isLoading}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="expert">Expert</option>
          </select>
        </div>

        <div className="form-group">
          <label>Learning Style:</label>
          <select
            value={personalizationSettings.learningStyle}
            onChange={(e) => handleSettingChange('learningStyle', e.target.value)}
            disabled={isLoading}
          >
            <option value="examples_and_applications">Examples & Applications</option>
            <option value="theoretical">Theoretical</option>
            <option value="practical">Practical</option>
            <option value="visual">Visual</option>
          </select>
        </div>

        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={personalizationSettings.backgroundMatching}
              onChange={(e) => handleSettingChange('backgroundMatching', e.target.checked)}
              disabled={isLoading}
            />
            Match content to my background
          </label>
        </div>

        <div className="form-group">
          <label>Preferred Language:</label>
          <select
            value={personalizationSettings.preferredLanguage}
            onChange={(e) => handleSettingChange('preferredLanguage', e.target.value)}
            disabled={isLoading}
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
          </select>
        </div>

        <div className="personalization-actions">
          <button
            onClick={handleSaveSettings}
            disabled={isLoading}
            className="save-settings-button"
          >
            {isLoading ? 'Saving...' : 'Save Settings'}
          </button>

          <button
            onClick={handlePersonalizeChapter}
            disabled={isLoading || !currentChapterId}
            className="personalize-chapter-button"
          >
            {isLoading ? 'Processing...' : 'Personalize Chapter'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PersonalizationPanel;