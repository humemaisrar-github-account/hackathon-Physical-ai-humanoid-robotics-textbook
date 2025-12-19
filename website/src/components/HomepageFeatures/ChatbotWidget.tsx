import React, { useState } from "react";

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Floating Button */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          position: "fixed",
          bottom: "20px",
          right: "20px",
          width: "60px",
          height: "60px",
          borderRadius: "50%",
          background: "linear-gradient(135deg,#0f2027,#203a43,#2c5364,#1c3d52)",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          zIndex: 9999,
          fontSize: "26px",
        }}
      >
        💬
      </div>

      {/* Popup */}
      {open && (
        <div
          style={{
            position: "fixed",
            bottom: "90px",
            right: "20px",
            width: "320px",
            height: "420px",
            background: "#0f2027",
            borderRadius: "12px",
            color: "white",
            zIndex: 9999,
            boxShadow: "0 0 20px rgba(0,0,0,0.4)",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div style={{ padding: "12px", borderBottom: "1px solid #203a43" }}>
             AI Assistant
          </div>

          <div style={{ flex: 1, padding: "10px", fontSize: "14px" }}>
            Hello! Chatbot UI is working 
          </div>

          <input
            placeholder="Type message..."
            style={{
              border: "none",
              outline: "none",
              padding: "10px",
              borderTop: "1px solid #203a43",
            }}
          />
        </div>
      )}
    </>
  );
}
