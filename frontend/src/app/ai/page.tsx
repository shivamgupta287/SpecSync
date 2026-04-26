"use client";

import { useState } from "react";
import Link from "next/link";
import { api, type RecommendResult } from "@/lib/api";

export default function AIRecommendPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<RecommendResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.ai.recommend(query.trim());
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <Link href="/" className="text-blue-400 hover:text-blue-300 text-sm mb-6 inline-block">
        ← Back to search
      </Link>

      <h1 className="text-3xl font-bold text-white mb-2">AI Recommend</h1>
      <p className="text-gray-400 mb-8">
        Describe what you want in plain English — Claude will find the best match on GSMArena.
      </p>

      <form onSubmit={handleSubmit} className="flex gap-2 mb-8">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='e.g. "best camera phone under $500 with long battery life"'
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          {loading ? "Thinking…" : "Ask AI"}
        </button>
      </form>

      {error && <p className="text-red-400 mb-6">Error: {error}</p>}

      {result && (
        <div className="flex flex-col gap-6">
          <div className="bg-purple-950 border border-purple-800 rounded-lg p-5">
            <p className="text-xs text-purple-400 uppercase font-semibold mb-2">
              Claude searched for
            </p>
            <p className="text-white font-medium">"{result.search_term}"</p>
          </div>

          <div className="bg-gray-900 border border-gray-700 rounded-lg p-5">
            <p className="text-xs text-gray-400 uppercase font-semibold mb-3">
              AI Recommendation
            </p>
            <p className="text-gray-100 leading-relaxed">{result.recommendation}</p>
          </div>

          <div>
            <p className="text-xs text-gray-400 uppercase font-semibold mb-3">
              Top Candidates
            </p>
            <div className="grid gap-2">
              {result.candidates.map((c) => (
                <Link
                  key={c.url}
                  href={`/phone?url=${encodeURIComponent(c.url)}`}
                  className="flex items-center justify-between bg-gray-900 hover:bg-gray-800 border border-gray-800 rounded-lg px-5 py-3 transition-colors"
                >
                  <span className="text-white">{c.name}</span>
                  <span className="text-gray-500 text-sm">View specs →</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
