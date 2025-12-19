import React from "react";
import Layout from "@theme-original/Layout";
import ChatbotWidget from "../../components/HomepageFeatures/ChatbotWidget";

export default function LayoutWrapper(props) {
  return (
    <>
      <Layout {...props} />
      <ChatbotWidget />
    </>
  );
}
