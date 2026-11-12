import type { Source } from "@/types/trip";

export default function SourceList({ sources }: { sources: Source[] }) {
  if (sources.length === 0) return null;
  return (
    <div className="rounded-3xl bg-slate-100/70 p-5">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Sources from the dataset
      </p>
      <div className="flex flex-wrap gap-2">
        {sources.map((s) => (
          <span
            key={s.id}
            className="rounded-full bg-white px-3 py-1 text-xs text-slate-600 ring-1 ring-slate-200"
          >
            {s.place}
          </span>
        ))}
      </div>
    </div>
  );
}
