"use client";
import { useState } from "react";
import { askQuestion } from "@/lib/api";

const SUGGESTIONS = [
  "Who are the top 5 scorers?",
  "How does xG affect match outcomes?",
  "Compare Arsenal vs Chelsea stats",
  "Which players are underperforming?",
  "What is the average market value by position?",
];

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<{ q: string; a: string; src: string }[]>([]);

  const handleAsk = async (q?: string) => {
    const query = q || question;
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await askQuestion(query);
      setResult(res);
      setHistory(prev => [...prev, { q: query, a: res.answer, src: res.source }]);
    } catch {
      setResult({ answer: "Something went wrong", source: "error" });
    }
    setLoading(false);
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Ask AI</h1>
      <p className="text-zinc-400">Ask questions in natural language — SQL or RAG-powered answers</p>

      {/* Input */}
      <div className="flex gap-3">
        <input
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleAsk()}
          placeholder="e.g. Who are the top 10 most valuable players?"
          className="flex-1 bg-zinc-900 rounded-lg px-4 py-3 border border-zinc-700 focus:border-emerald-500 outline-none text-lg"
        />
        <button onClick={() => handleAsk()} disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 px-8 py-3 rounded-lg font-medium transition">
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {/* Suggestions */}
      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map(s => (
          <button key={s} onClick={() => { setQuestion(s); handleAsk(s); }}
            className="text-xs bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 px-3 py-1.5 rounded-full transition">
            {s}
          </button>
        ))}
      </div>

      {/* Current Result */}
      {result && (
        <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
          <div className="flex items-center gap-2 mb-3">
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${
              result.source === "sql" ? "bg-blue-500/20 text-blue-400" :
              result.source === "rag" ? "bg-purple-500/20 text-purple-400" : "bg-zinc-700 text-zinc-400"
            }`}>
              {result.source?.toUpperCase()}
            </span>
          </div>
          <p className="text-lg leading-relaxed">{result.answer}</p>
          {result.data && result.data.length > 0 && (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-zinc-700">
                    {Object.keys(result.data[0]).map(k => (
                      <th key={k} className="text-left p-2 text-zinc-500">{k}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.data.map((row: any, i: number) => (
                    <tr key={i} className="border-b border-zinc-800">
                      {Object.values(row).map((v: any, j: number) => (
                        <td key={j} className="p-2">{typeof v === "number" ? v.toFixed?.(2) ?? v : v}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* History */}
      {history.length > 1 && (
        <section>
          <h3 className="text-lg font-semibold mb-3">History</h3>
          <div className="space-y-2">
            {history.slice(0, -1).reverse().map((h, i) => (
              <div key={i} className="bg-zinc-900/50 rounded p-3 border border-zinc-800">
                <p className="text-sm text-zinc-400">Q: {h.q}</p>
                <p className="text-sm mt-1">{h.a.slice(0, 150)}...</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}