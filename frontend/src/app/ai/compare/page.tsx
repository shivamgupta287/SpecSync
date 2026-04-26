"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api, type CompareResult } from "@/lib/api";

export default function ComparePage() {
  const params = useSearchParams();

  // Pre-filled from /phone page
  const p1 = params.get("p1") ?? "";
  const p1name = params.get("p1name") ?? "";

  const [url1, setUrl1] = useState(p1);
  const [url2, setUrl2] = useState("");
  const [result, setResult] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Auto-trigger if both URLs are ready from query params
  useEffect(() => {
    const p2 = params.get("p2");
    if (p1 && p2) {
      setUrl2(p2);
      runCompare(p1, p2);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function runCompare(u1: string, u2: string) {
    if (!u1.trim() || !u2.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await api.ai.compare(u1.trim(), u2.trim()));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault();
    runCompare(url1, url2);
  }

  return (
    <div className="max-w-2xl">
      <Link href="/" className="text-blue-400 hover:text-blue-300 text-sm mb-6 inline-block">
        ← Back to search
      </Link>

      <h1 className="text-3xl font-bold text-white mb-2">Compare Phones</h1>
      <p className="text-gray-400 mb-8">Paste two GSMArena phone URLs — Claude will compare them.</p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3 mb-8">
        <input
          type="text"
          value={url1}
          onChange={(e) => setUrl1(e.target.value)}
          placeholder="GSMArena URL for phone 1"
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        {p1name && <p className="text-gray-500 text-xs -mt-1 ml-1">Pre-filled: {p1name}</p>}
        <input
          type="text"
          value={url2}
          onChange={(e) => setUrl2(e.target.value)}
          placeholder="GSMArena URL for phone 2"
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <button
          type="submit"
          disabled={loading || !url1.trim() || !url2.trim()}
          className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          {loading ? "Comparing…" : "Compare"}
        </button>
      </form>

      {error && <p className="text-red-400 mb-6">Error: {error}</p>}

      {result && (
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-2 gap-4 text-sm">
            {([result.phone1, result.phone2] as const).map((phone) => (
              <div key={phone.url} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <p className="font-semibold text-white mb-2">{phone.name}</p>
                {Object.entries(phone.specs)
                  .slice(0, 8)
                  .map(([k, v]) => (
                    <div key={k} className="flex flex-col mb-1">
                      <span className="text-gray-500 text-xs">{k}</span>
                      <span className="text-gray-200 text-xs">{v}</span>
                    </div>
                  ))}
              </div>
            ))}
          </div>

          <div className="bg-purple-950 border border-purple-800 rounded-lg p-5">
            <p className="text-xs text-purple-400 uppercase font-semibold mb-3">AI Comparison</p>
            <p className="text-gray-100 leading-relaxed whitespace-pre-wrap">{result.comparison}</p>
          </div>
        </div>
      )}
    </div>
  );
}
