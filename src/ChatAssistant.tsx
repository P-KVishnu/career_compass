import React, { useState } from "react";

interface ChatAssistantProps {
  resultData: any; // Contains career, recommendations, mentors, jobs
}

const ChatAssistant: React.FC<ChatAssistantProps> = ({ resultData }) => {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([
    { role: "assistant", content: "👋 Hi there! I’m your AI Career Assistant. Ask me anything about your career path!" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const backendUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${backendUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          career: resultData?.career,
          recommendations: resultData?.recommendations || [],
          mentors: resultData?.mentors || [],
          jobs: resultData?.jobs || [],
        }),
      });

      const data = await res.json();

      if (res.ok && data.reply) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "⚠️ Sorry, I couldn't get a response right now. Please try again.",
          },
        ]);
      }
    } catch (error) {
      console.error("❌ Chat fetch error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "❌ Oops! There was a network error. Please try again later.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-10 p-6 bg-gray-50 border rounded-2xl shadow-md max-w-3xl mx-auto">
      <h3 className="text-2xl font-semibold mb-4 text-gray-800">
        💬 AI Career Assistant
      </h3>

      <div className="h-80 overflow-y-auto border rounded-lg p-4 bg-white space-y-3">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`px-4 py-2 rounded-xl max-w-xs ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-gray-500 italic text-sm">AI is typing...</div>
        )}
      </div>

      <form onSubmit={sendMessage} className="mt-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a career question..."
          className="flex-grow border px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default ChatAssistant;
