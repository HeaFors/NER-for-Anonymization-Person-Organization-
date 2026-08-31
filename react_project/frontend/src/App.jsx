import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([
  { id: 1, sender: 'bot', text: 'Вітаю! Я AI Entity Analyst. Чим можу допомогти?' }
]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
  e?.preventDefault();
  if (!input.trim() || loading) return;

  const userQuery = input;
  const userMsg = { id: Date.now(), sender: 'user', text: userQuery };

  setMessages((prev) => [...prev, userMsg]);
  setInput('');
  setLoading(true);

  try {
    const res = await fetch('http://127.0.0.1:8000/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: userQuery })
    });

    if (!res.ok) throw new Error('Помилка сервера');

    const data = await res.json();

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.response || data.data || "Порожня відповідь від сервера"
      }
    ]);
  } catch (err) {
    console.error(err);
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now() + 1,
        sender: 'bot',
        text: "Помилка зв'язку з бекендом. Перевірте, чи працює uvicorn."
      }
    ]);
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="flex flex-col h-screen bg-[#181d2a] text-slate-100 font-sans overflow-hidden">
      {/* Header */}
      <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-[#1a1f2c]/50 backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="text-teal-400 font-bold text-xl flex items-center justify-center w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/20">
            Ai
          </div>
          <h1 className="text-xl font-bold tracking-wide text-white">AI Entity Analyst</h1>
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
            BERT + FAISS RAG
          </span>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 max-w-3xl ${
                msg.sender === 'user' ? 'ml-auto flex-row-reverse space-x-reverse' : ''
              }`}
            >
              {msg.sender === 'bot' && (
                <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 text-teal-400 shadow-md">
                  <Bot className="w-5 h-5" />
                </div>
              )}

              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-line shadow-lg transition-all ${
                  msg.sender === 'user'
                    ? 'bg-gradient-to-r from-teal-600 to-emerald-600 text-white rounded-tr-none'
                    : 'bg-[#222838] text-slate-200 border border-slate-700/60 rounded-tl-none'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center space-x-3 text-slate-400 text-sm">
              <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-teal-400 animate-pulse">
                <Bot className="w-5 h-5" />
              </div>
              <div className="flex space-x-1.5 p-3 bg-[#222838] rounded-xl border border-slate-700/60">
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Bar */}
      <div className="p-4 bg-[#1a1f2c]/80 border-t border-slate-800/80">
        <form
          onSubmit={handleSend}
          className="max-w-4xl mx-auto flex items-center bg-[#22283c] border border-slate-700/70 rounded-2xl px-4 py-2 focus-within:border-teal-500/70 transition-all shadow-xl"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Запитайте про сутності..."
            className="flex-1 bg-transparent text-slate-100 placeholder-slate-400 focus:outline-none text-sm px-2 py-2"
          />

          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="flex items-center space-x-2 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-semibold px-4 py-2 rounded-xl transition-all shadow-lg hover:shadow-teal-500/20 disabled:opacity-50 disabled:cursor-not-allowed ml-2"
          >
            <Send className="w-4 h-4" />
            <span className="text-xs">Надіслати</span>
          </button>
        </form>
      </div>
    </div>
  );
}