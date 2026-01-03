/**
 * API client for the RAG Chatbot frontend
 */

class ApiClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  /**
   * Make a request to the backend API
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  /**
   * Send a message to the RAG chatbot
   */
  async sendMessage(message, sessionId, mode = 'book-wide', selectedText = null) {
    const requestBody = {
      message: message,
      session_id: sessionId,
      mode: mode,
    };

    if (mode === 'selected-text-only' && selectedText) {
      requestBody.selected_text = selectedText;
    }

    return this.request('/rag/chat', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  /**
   * Query with selected text context
   */
  async queryWithSelectedText(query, selectedText, userId = null) {
    const requestBody = {
      query: query,
      selected_text: selectedText,
    };

    if (userId) {
      requestBody.user_id = userId;
    }

    return this.request('/rag/query', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  /**
   * Register a new user
   */
  async registerUser(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  /**
   * Login a user
   */
  async loginUser(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  /**
   * Get personalized chapter content
   */
  async getPersonalizedChapter(chapterId, userId) {
    const params = new URLSearchParams({ user_id: userId });
    return this.request(`/personalization/chapter/${chapterId}?${params}`);
  }

  /**
   * Translate content to Urdu
   */
  async translateToUrdu(content, chapterId, userId = null) {
    const requestBody = {
      content: content,
      chapter_id: chapterId,
    };

    if (userId) {
      requestBody.user_id = userId;
    }

    return this.request('/translation/urdu', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  /**
   * Check API health
   */
  async healthCheck() {
    return this.request('/health');
  }
}

// Create a singleton instance
const apiClient = new ApiClient();

export default apiClient;