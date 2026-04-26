"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type Mode = "phone" | "brand";

export default function HomePage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("phone");
  const [query, setQuery] = useState("");

  function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault();
    if (!query.trim()) return;
    if (mode === "phone") {
      router.push(`/phone?q=${encodeURIComponent(query.trim())}`);
    } else {
      router.push(`/brand?q=${encodeURIComponent(query.trim())}`);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-2">SpecSync</h1>
        <p className="text-gray-400">Search phones and brands — powered by GSMArena &amp; Claude AI</p>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-xl flex flex-col gap-4">
        {/* Mode toggle */}
        <div className="flex rounded-lg overflow-hidden border border-gray-700 w-fit mx-auto">
          {(["phone", "brand"] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className={`px-5 py-2 text-sm font-medium capitalize transition-colors ${
                mode === m
                  ? "bg-blue-600 text-white"
                  : "bg-gray-900 text-gray-400 hover:text-white"
              }`}
            >
              {m}
            </button>
          ))}
        </div>

        {/* Search input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              mode === "phone"
                ? 'e.g. "Samsung Galaxy S24"'
                : 'e.g. "OnePlus"'
            }
            className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Search
          </button>
        </div>
      </form>

      <p className="text-gray-600 text-sm">
        Or try{" "}
        <a href="/ai" className="text-blue-400 hover:text-blue-300 underline">
          AI Recommend
        </a>{" "}
        — describe what you want in plain English
      </p>
    </div>
  );
}
