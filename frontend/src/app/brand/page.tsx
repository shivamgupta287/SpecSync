"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api, type Brand, type Phone } from "@/lib/api";

export default function BrandPage() {
  const params = useSearchParams();
  const q = params.get("q") ?? "";

  const [brand, setBrand] = useState<Brand | null>(null);
  const [phones, setPhones] = useState<Phone[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!q) return;
    setLoading(true);
    setError("");
    api.brands
      .phones(q, 20)
      .then((data) => {
        setBrand(data.brand);
        setPhones(data.phones);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [q]);

  if (loading)
    return <p className="text-gray-400 animate-pulse">Fetching phones for "{q}"…</p>;
  if (error)
    return <p className="text-red-400">Error: {error}</p>;

  return (
    <div>
      <Link href="/" className="text-blue-400 hover:text-blue-300 text-sm mb-6 inline-block">
        ← Back to search
      </Link>

      {brand && (
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">{brand.name}</h1>
          <p className="text-gray-400 mt-1">{brand.phone_count} devices total · showing {phones.length}</p>
        </div>
      )}

      <div className="grid gap-3">
        {phones.map((phone) => (
          <Link
            key={phone.url}
            href={`/phone?url=${encodeURIComponent(phone.url)}`}
            className="flex items-center justify-between bg-gray-900 hover:bg-gray-800 border border-gray-800 rounded-lg px-5 py-4 transition-colors"
          >
            <span className="text-white font-medium">{phone.name}</span>
            <span className="text-gray-500 text-sm">View specs →</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
