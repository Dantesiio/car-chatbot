import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Send a greeting message when the application starts
  useEffect(() => {
    const greetingMessage = { sender: "Chatbot", text: "Hello! Welcome to the Car Troubleshooting Assistant. How can I help you today?" };
    setMessages([greetingMessage]);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "User", text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await axios.post("http://localhost:8000/api/chat", { message: input });
      const botMessage = { sender: "Chatbot", text: response.data.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = { sender: "Chatbot", text: "I'm sorry, an error occurred while processing your request." };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setInput("");
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <h1>Car Troubleshooting Assistant</h1>
        <div className="chat-box">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender === "User" ? "user" : "chatbot"}`}>
              <b>{msg.sender}:</b> {msg.text}
            </div>
          ))}
        </div>
        <div className="input-container">
          <input
            type="text"
            placeholder="Describe the issue here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
