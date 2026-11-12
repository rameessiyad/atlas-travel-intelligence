"use client";

import { useState } from "react";
import { inputClass, primaryButton } from "@/lib/styles";

const SUGGESTIONS = [
  "Make day 2 less busy",
  "Add more food",
  "Reduce the budget",
  "More outdoor activities",
];

interface Props {
  loading: boolean;
  onRevise: (change: string) => Promise<boolean>;
}

export default function ReviseBox({ loading, onRevise }: Props) {
  const [change, setChange] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!change.trim()) return;
    const ok = await onRevise(change);
    if (ok) setChange("");
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-3xl bg-white p-5 shadow-lg shadow-slate-200/50 ring-1 ring-slate-100"
    >
      <p className="mb-3 text-sm font-semibold text-slate-900">
        Want to change something?
      </p>
      <div className="mb-3 flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setChange(s)}
            className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600 transition hover:bg-indigo-50 hover:text-indigo-600"
          >
            {s}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className={inputClass}
          placeholder="Describe the change..."
          value={change}
          onChange={(e) => setChange(e.target.value)}
        />
        <button
          type="submit"
          disabled={loading}
          className={`${primaryButton} shrink-0 !py-2.5`}
        >
          {loading ? "Revising..." : "Revise"}
        </button>
      </div>
    </form>
  );
}
