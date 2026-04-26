const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Brand {
  name: string;
  url: string;
  phone_count: number;
}

export interface Phone {
  name: string;
  url: string;
  score?: number;
}

export interface PhoneSpecs {
  name: string;
  url: string;
  image_url?: string;
  specs: Record<string, string>;
}

export interface RecommendResult {
  query: string;
  search_term: string;
  candidates: Phone[];
  recommendation: string;
}

export interface CompareResult {
  phone1: { name: string; url: string; specs: Record<string, string> };
  phone2: { name: string; url: string; specs: Record<string, string> };
  comparison: string;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json();
}

export const api = {
  brands: {
    search: (q: string) =>
      get<{ brand: Brand }>(`/api/brands/search?q=${encodeURIComponent(q)}`),
    phones: (name: string, limit = 20) =>
      get<{ brand: Brand; phones: Phone[] }>(
        `/api/brands/${encodeURIComponent(name)}/phones?limit=${limit}`
      ),
  },
  phones: {
    search: (q: string) =>
      get<{ query: string; candidates: Phone[] }>(
        `/api/phones/search?q=${encodeURIComponent(q)}`
      ),
    specs: (url: string) =>
      get<PhoneSpecs>(`/api/phones/specs?url=${encodeURIComponent(url)}`),
  },
  ai: {
    recommend: (query: string) =>
      post<RecommendResult>("/api/ai/recommend", { query }),
    compare: (phone1_url: string, phone2_url: string) =>
      post<CompareResult>("/api/ai/compare", { phone1_url, phone2_url }),
  },
};
