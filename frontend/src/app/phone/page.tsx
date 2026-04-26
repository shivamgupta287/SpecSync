"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, type Phone, type PhoneSpecs } from "@/lib/api";

export default function PhonePage() {
  const params = useSearchParams();
  const router = useRouter();

  const q = params.get("q") ?? "";
  const url = params.get("url") ?? "";

  const [candidates, setCandidates] = useState<Phone[]>([]);
  const [specs, setSpecs] = useState<PhoneSpecs | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // If we have a direct URL, fetch specs immediately
  useEffect(() => {
    if (!url) return;
    setLoading(true);
    api.phones
      .specs(url)
      .then(setSpecs)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [url]);

  // If we have a query, search for candidates
  useEffect(() => {
    if (!q || url) return;
    setLoading(true);
    api.phones
      .search(q)
      .then((data) => {
        if (data.candidates.length === 1) {
          // Single match — go straight to specs
          router.replace(`/phone?url=${encodeURIComponent(data.candidates[0].url)}`);
        } else {
          setCandidates(data.candidates);
          setLoading(false);
        }
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [q, url, router]);

  if (loading)
    return <p className="text-gray-400 animate-pulse">Searching…</p>;
  if (error)
    return <p className="text-red-400">Error: {error}</p>;

  // Disambiguation list
  if (candidates.length > 0)
    return (
      <div>
        <Link href="/" className="text-blue-400 hover:text-blue-300 text-sm mb-6 inline-block">
          ← Back to search
        </Link>
        <h1 className="text-2xl font-bold text-white mb-2">Multiple matches for "{q}"</h1>
        <p className="text-gray-400 mb-6">Select the phone you meant:</p>
        <div className="grid gap-3">
          {candidates.map((c) => (
            <Link
              key={c.url}
              href={`/phone?url=${encodeURIComponent(c.url)}`}
              className="flex items-center justify-between bg-gray-900 hover:bg-gray-800 border border-gray-800 rounded-lg px-5 py-4 transition-colors"
            >
              <span className="text-white font-medium">{c.name}</span>
              <span className="text-gray-500 text-sm">score {c.score?.toFixed(2)}</span>
            </Link>
          ))}
        </div>
      </div>
    );

  if (!specs) return null;

  return (
    <div>
      <Link href="/" className="text-blue-400 hover:text-blue-300 text-sm mb-6 inline-block">
        ← Back to search
      </Link>

      <div className="flex gap-6 items-start mb-8">
        {specs.image_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={specs.image_url} alt={specs.name} className="w-32 object-contain rounded-lg bg-gray-900 p-2" />
        )}
        <div>
          <h1 className="text-3xl font-bold text-white">{specs.name}</h1>
          <a href={specs.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-sm mt-1 inline-block">
            View on GSMArena ↗
          </a>
          <Link
            href={`/ai/compare?p1=${encodeURIComponent(specs.url)}&p1name=${encodeURIComponent(specs.name)}`}
            className="ml-4 text-purple-400 hover:text-purple-300 text-sm mt-1 inline-block"
          >
            + Compare with another phone
          </Link>
        </div>
      </div>

      <div className="rounded-lg border border-gray-800 overflow-hidden">
        {Object.entries(specs.specs).map(([label, value], i) => (
          <div
            key={label}
            className={`flex px-5 py-3 text-sm ${i % 2 === 0 ? "bg-gray-900" : "bg-gray-950"}`}
          >
            <span className="w-56 shrink-0 text-gray-400">{label}</span>
            <span className="text-white">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
