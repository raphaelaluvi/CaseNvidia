import { useState } from "react";

export function ChatPanel({ messages, onSendMessage, isSending = false, disabled = false }) {
  const [input, setInput] = useState("");

  const submitMessage = () => {
    if (disabled || isSending) return;
    onSendMessage(input);
    setInput("");
  };

  return (
    <section className="panel chat-panel">
      <div className="section-heading">
        <div>
          <p className="section-label">Chat de consulta</p>
          <h2>Radar assistente</h2>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            {disabled
              ? "Selecione ou analise uma startup para habilitar o chat com LLM."
              : "Nenhuma mensagem ainda. Use o campo abaixo para iniciar uma consulta."}
          </div>
        ) : null}
        {messages.map((message) => (
          <article key={message.id} className={`chat-bubble ${message.role}`}>
            <span>{message.role === "assistant" ? "Radar" : "Você"}</span>
            <p>{message.text}</p>
          </article>
        ))}
      </div>

      <div className="chat-input">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Pergunte sobre fit NVIDIA, sinais de IA ou recomendações..."
          rows={3}
          disabled={disabled || isSending}
        />
        <button className="button primary" type="button" onClick={submitMessage} disabled={disabled || isSending}>
          {isSending ? "Consultando..." : "Enviar"}
        </button>
      </div>
    </section>
  );
}
