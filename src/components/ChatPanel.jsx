import { useState } from "react";

const suggestions = [
  "Quais startups tem maior aderencia ao ecossistema NVIDIA?",
  "Mostre empresas de healthtech com potencial de IA generativa",
  "Quais produtos NVIDIA fazem mais sentido para esta startup?",
];

export function ChatPanel({ messages, onSendMessage }) {
  const [input, setInput] = useState("");

  const submitMessage = () => {
    onSendMessage(input);
    setInput("");
  };

  return (
    <section className="panel chat-panel">
      <div className="section-heading">
        <div>
          <p className="section-label">Chat de consulta</p>
          <h2>Radar assistant</h2>
        </div>
      </div>

      <div className="suggestion-row">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            className="suggestion-chip"
            type="button"
            onClick={() => onSendMessage(suggestion)}
          >
            {suggestion}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <article key={message.id} className={`chat-bubble ${message.role}`}>
            <span>{message.role === "assistant" ? "Radar" : "Voce"}</span>
            <p>{message.text}</p>
          </article>
        ))}
      </div>

      <div className="chat-input">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Pergunte sobre fit NVIDIA, sinais de IA ou recomendacoes..."
          rows={3}
        />
        <button className="button primary" type="button" onClick={submitMessage}>
          Enviar
        </button>
      </div>
    </section>
  );
}
