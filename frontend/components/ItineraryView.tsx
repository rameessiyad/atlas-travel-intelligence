import { parseItinerary } from "@/lib/api/parseItinerary";

export default function ItineraryView({ text }: { text: string }) {
  const sections = parseItinerary(text);

  return (
    <div className="space-y-4">
      {sections.map((s, i) => (
        <article
          key={i}
          className="rounded-3xl bg-white p-6 shadow-lg shadow-slate-200/50 ring-1 ring-slate-100"
        >
          <div className="mb-3 flex items-center gap-3">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-50 text-sm font-bold text-indigo-600">
              {i + 1}
            </span>
            <h3 className="font-semibold text-slate-900">{s.title}</h3>
          </div>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600">
            {s.body}
          </p>
        </article>
      ))}
    </div>
  );
}
