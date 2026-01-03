import React from 'react';
import PopupChatbot from '@site/src/components/PopupChatbot';

// Root component that wraps the entire application
// This ensures the PopupChatbot appears on all pages and persists during navigation
const Root = ({ children }) => {
  return (
    <>
      {children}
      <PopupChatbot />
    </>
  );
};

export default Root;