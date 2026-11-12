"use client";

import { useState } from "react";
import { inputClass, primaryButton } from "@/lib/styles";
import type { Pace, TripRequest } from "@/types/trip";

const PACES: Pace[] = ["Relaxed", "Balanced", "Busy"];
const INTERESTS = [
  "Food",
  "Art",
  "History",
  "Nature",
  "Nightlife",
  "Shopping",
  "Beaches",
];

interface Props {
  loading: boolean;
  onSubmit: (trip: TripRequest) => void;
}

export default function TripForm({ loading, onSubmit }: Props) {
  const [form, setForm] = useState<TripRequest>({
    destination: "",
    days: 3,
    budget: "",
    interests: "",
    pace: "Balanced",
    extra: "",
  });
  const [touched, setTouched] = useState(false);

  const set = <K extends keyof TripRequest>(key: K, value: TripRequest[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const selected = form.interests
    .split(",")
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);

  function toggleInterest(name: string) {
    const lower = name.toLowerCase();
    const next = selected.includes(lower)
      ? selected.filter((s) => s !== lower)
      : [...selected, lower];
    set("interests", next.join(", "));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched(true);
    if (form.destination.trim()) onSubmit(form);
  }

  const label =
    "mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500";

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-5 rounded-3xl bg-white p-6 shadow-xl shadow-slate-200/60 ring-1 ring-slate-100"
    >
      <div>
        <label className={label}>Destination</label>
        <input
          className={inputClass}
          placeholder="Paris, Kyoto, Bali..."
          value={form.destination}
          onChange={(e) => set("destination", e.target.value)}
        />
        {touched && !form.destination.trim() && (
          <p className="mt-1 text-xs text-rose-600">
            Please enter a destination.
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={label}>Days</label>
          <input
            className={inputClass}
            type="number"
            min={1}
            max={30}
            value={form.days}
            onChange={(e) =>
              set(
                "days",
                Math.min(30, Math.max(1, Number(e.target.value) || 1)),
              )
            }
          />
        </div>
        <div>
          <label className={label}>Budget</label>
          <input
            className={inputClass}
            placeholder="e.g. moderate"
            value={form.budget}
            onChange={(e) => set("budget", e.target.value)}
          />
        </div>
      </div>

      <div>
        <label className={label}>Pace</label>
        <div className="grid grid-cols-3 gap-1 rounded-xl bg-slate-100 p-1">
          {PACES.map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => set("pace", p)}
              className={`rounded-lg py-2 text-sm font-medium transition ${
                form.pace === p
                  ? "bg-white text-indigo-600 shadow-sm"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className={label}>Interests</label>
        <div className="mb-2 flex flex-wrap gap-2">
          {INTERESTS.map((name) => {
            const on = selected.includes(name.toLowerCase());
            return (
              <button
                key={name}
                type="button"
                onClick={() => toggleInterest(name)}
                className={`rounded-full px-3 py-1 text-xs font-medium ring-1 transition ${
                  on
                    ? "bg-indigo-600 text-white ring-indigo-600"
                    : "bg-white text-slate-600 ring-slate-200 hover:ring-indigo-300"
                }`}
              >
                {name}
              </button>
            );
          })}
        </div>
        <input
          className={inputClass}
          placeholder="Or type your own..."
          value={form.interests}
          onChange={(e) => set("interests", e.target.value)}
        />
      </div>

      <div>
        <label className={label}>Anything else?</label>
        <textarea
          className={inputClass}
          rows={2}
          placeholder="Avoid long walks, include local food..."
          value={form.extra}
          onChange={(e) => set("extra", e.target.value)}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className={`${primaryButton} w-full`}
      >
        {loading ? "Planning your trip..." : "Create itinerary"}
      </button>
    </form>
  );
}
