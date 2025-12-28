import React from "react";
import Layout from "@theme-original/Layout";
import ChatbotPopup from "../../components/ChatbotPopup"; // Updated import path

export default function LayoutWrapper(props) {
  return (
    <>
      <Layout {...props} />
      <ChatbotPopup /> {/* Render the ChatbotPopup */}
    </>
  );
}
