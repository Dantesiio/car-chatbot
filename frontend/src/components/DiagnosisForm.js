import React, { useState, useEffect } from "react";
import axios from "axios";
import "./DiagnosisForm.css";

function DiagnosisForm() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");

  // Mensaje inicial del chatbot
  useEffect(() => {
    setMessages([
      { sender: "bot", text: "Welcome! Describe the issue with your car, and I'll help diagnose it." },
    ]);
  }, []);

  const sendMessage = async () => {
    if (!userInput) return;

    // Agregar el mensaje del usuario al chat
    setMessages((prev) => [...prev, { sender: "user", text: userInput }]);

    try {
      // Enviar el mensaje del usuario al backend
      const response = await axios.post("http://localhost:8000/api/chat", {
        message: userInput,
      });

      // Obtener la respuesta del chatbot
      const botResponse = response.data.response;

      // Agregar la respuesta del chatbot al chat
      setMessages((prev) => [...prev, { sender: "bot", text: botResponse }]);
    } catch (error) {
      console.error("Error communicating with the chatbot:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "I'm sorry, an error occurred while processing your request." },
      ]);
    }

    // Limpiar la entrada del usuario
    setUserInput("");
  };

  return (
    <div className="chat-container">
      <h1>Diagnóstico de Problemas en Automóviles</h1>
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-message ${
              msg.sender === "user" ? "user-message" : "bot-message"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Describe el problema aquí..."
        />
        <button onClick={sendMessage}>Enviar</button>
      </div>
    </div>
  );
}

export default DiagnosisForm;
