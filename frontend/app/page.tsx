"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Source = { id: string; place: string; source: string };

export default function Home() {
  const [form, setForm] = useState({
    destination: "",
    days: 3,
    budget: "",
    interests: "",
    pace: "Balanced",
    extra: "",
  });
  const [itinerary, setItinerary] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const update = (key: string, value: string | number) =>
    setForm((f) => ({ ...f, [key]: value }));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.destination.trim()) {
      setError("Please enter a destination.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API}/itinerary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      setItinerary(data.itinerary);
      setSources(data.sources);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  const input =
    "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";

  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="text-3xl font-bold">Atlas</h1>
      <p className="mb-6 text-gray-500">Personal Travel Intelligence</p>

      <form onSubmit={submit} className="space-y-3">
        <input
          className={input}
          placeholder="Destination (e.g. Paris)"
          value={form.destination}
          onChange={(e) => update("destination", e.target.value)}
        />
        <div className="grid grid-cols-2 gap-3">
          <input
            className={input}
            type="number"
            min={1}
            max={30}
            value={form.days}
            onChange={(e) => update("days", Number(e.target.value))}
          />
          <select
            className={input}
            value={form.pace}
            onChange={(e) => update("pace", e.target.value)}
          >
            <option>Relaxed</option>
            <option>Balanced</option>
            <option>Busy</option>
          </select>
        </div>
        <input
          className={input}
          placeholder="Budget (e.g. moderate)"
          value={form.budget}
          onChange={(e) => update("budget", e.target.value)}
        />
        <input
          className={input}
          placeholder="Interests (e.g. art, food)"
          value={form.interests}
          onChange={(e) => update("interests", e.target.value)}
        />
        <textarea
          className={input}
          rows={2}
          placeholder="Anything else?"
          value={form.extra}
          onChange={(e) => update("extra", e.target.value)}
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-blue-600 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Planning your trip..." : "Create itinerary"}
        </button>
      </form>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      {itinerary && (
        <section className="mt-8">
          <h2 className="mb-2 text-xl font-semibold">Your itinerary</h2>
          <div className="whitespace-pre-wrap rounded-lg bg-gray-50 p-4 text-sm text-gray-900">
            {itinerary}
          </div>
          {sources.length > 0 && (
            <>
              <h3 className="mt-4 font-semibold">Sources from the dataset</h3>
              <ul className="list-disc pl-5 text-sm text-gray-600">
                {sources.map((s) => (
                  <li key={s.id}>
                    {s.place} <span className="text-gray-400">({s.id})</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      )}
    </main>
  );
}
