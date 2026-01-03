import React, { useState } from 'react';
import './RagChatbot.css';

const Auth = ({ onLogin, onRegister, isAuthenticated, onLogout }) => {
  const [isLoginView, setIsLoginView] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [softwareBackground, setSoftwareBackground] = useState('');
  const [hardwareBackground, setHardwareBackground] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      if (isLoginView) {
        // Login
        await onLogin({ email, password });
      } else {
        // Register
        const userData = {
          email,
          name,
          password,
          software_background: softwareBackground ? JSON.parse(softwareBackground) : null,
          hardware_background: hardwareBackground ? JSON.parse(hardwareBackground) : null
        };
        await onRegister(userData);
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  if (isAuthenticated) {
    return (
      <div className="auth-component">
        <div className="auth-logged-in">
          <h3>Welcome back!</h3>
          <button onClick={onLogout} className="logout-button">Logout</button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-component">
      <div className="auth-toggle">
        <button
          className={isLoginView ? 'active' : ''}
          onClick={() => setIsLoginView(true)}
        >
          Login
        </button>
        <button
          className={!isLoginView ? 'active' : ''}
          onClick={() => setIsLoginView(false)}
        >
          Register
        </button>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        {!isLoginView && (
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required={!isLoginView}
              disabled={isLoading}
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>

        {!isLoginView && (
          <>
            <div className="form-group">
              <label htmlFor="softwareBackground">Software Background (JSON)</label>
              <textarea
                id="softwareBackground"
                value={softwareBackground}
                onChange={(e) => setSoftwareBackground(e.target.value)}
                placeholder='{"experience_level": "intermediate", "languages": ["Python", "JavaScript"]}'
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="hardwareBackground">Hardware Background (JSON)</label>
              <textarea
                id="hardwareBackground"
                value={hardwareBackground}
                onChange={(e) => setHardwareBackground(e.target.value)}
                placeholder='{"experience_level": "beginner", "interests": ["microcontrollers", "sensors"]}'
                disabled={isLoading}
              />
            </div>
          </>
        )}

        {error && <div className="error-message">{error}</div>}

        <button
          type="submit"
          className="auth-button"
          disabled={isLoading}
        >
          {isLoading ? 'Processing...' : (isLoginView ? 'Login' : 'Register')}
        </button>
      </form>
    </div>
  );
};

export default Auth;