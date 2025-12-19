import React, { useState } from "react";

type Msg = {
  role: "user" | "bot";
  text: string;
};

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Msg[]>([
    { role: "bot", text: "Hello 👋 How can I help you?" },
  ]);

  const sendMessage = () => {
    if (!input.trim()) return;

    // user msg
    const userMsg: Msg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    // dummy bot reply (for now)
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "✅ Message received (backend next)" },
      ]);
    }, 600);
  };

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
          background:
            "linear-gradient(135deg,#0f2027,#203a43,#2c5364,#1c3d52)",
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
          {/* Header */}
          <div
            style={{
              padding: "10px",
              borderBottom: "1px solid #203a43",
            }}
          >
            🤖 AI Assistant
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              padding: "10px",
              overflowY: "auto",
              fontSize: "14px",
            }}
          >
            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  marginBottom: "8px",
                  textAlign: m.role === "user" ? "right" : "left",
                }}
              >
                <span
                  style={{
                    display: "inline-block",
                    padding: "6px 10px",
                    borderRadius: "8px",
                    background:
                      m.role === "user" ? "#203a43" : "#2c5364",
                  }}
                >
                  {m.text}
                </span>
              </div>
            ))}
          </div>

          {/* Input */}
          <div
            style={{
              display: "flex",
              borderTop: "1px solid #203a43",
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Type message..."
              style={{
                flex: 1,
                padding: "10px",
                border: "none",
                outline: "none",
              }}
            />
            <button
              onClick={sendMessage}
              style={{
                padding: "0 14px",
                border: "none",
                background: "#203a43",
                color: "white",
                cursor: "pointer",
              }}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
