import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const API = "https://your-backend-name.onrender.com";
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Load chat history
  useEffect(() => {
    fetch(`${API}/history`)
      .then(res => res.json())
      .then(data => setMessages(data));
  }, []);

  // Send message on Enter or Button click
  async function sendMessage(e) {
    e.preventDefault();

    if (!input.trim()) return;

    const res = await fetch("https://chatapp-8qep.onrender.com/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    });

    const data = await res.json();

    setMessages(prev => [
      ...prev,
      ["user", input],
      ["ai", data.reply]
    ]);

    setInput("");
  }

  // Clear chat
  async function clearChat() {
    await fetch("https://chatapp-8qep.onrender.com/clear", { method: "POST" });
    setMessages([]);
  }

  return (
    <div className="container">

      <h2>Tanmay's Chat Assistant</h2>

      {/* FORM enables ENTER KEY SEND */}
      <form onSubmit={sendMessage}>

        <div className="chatBox">
          {messages.map((msg, i) => (
            <p key={i} className={msg[0]}>
              <b>{msg[0]}:</b> {msg[1]}
            </p>
          ))}
        </div>

        <div className="controls">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your message..."
          />

          <button type="submit">Send</button>

          <button type="button" onClick={clearChat}>
            Clear
          </button>
        </div>

      </form>

    </div>
  );
}

export default App;
