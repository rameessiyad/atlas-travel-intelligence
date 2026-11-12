"use client";

import Header from "@/components/Header";
import TripForm from "@/components/TripForm";
import ItineraryView from "@/components/ItineraryView";
import ReviseBox from "@/components/ReviseBox";
import SourceList from "@/components/SourceList";
import Skeleton from "@/components/Skeleton";
import { useAtlas } from "@/hooks/useAtlas";

export default function Home() {
  const { itinerary, sources, status, error, generate, revise } = useAtlas();
  const generating = status === "generating";
  const revising = status === "revising";

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute -top-40 left-1/2 h-[480px] w-[900px] -translate-x-1/2 rounded-full bg-[radial-gradient(closest-side,rgba(99,102,241,0.22),transparent)]" />

      <main className="relative mx-auto max-w-6xl px-5 py-8 sm:px-8">
        <Header />

        <section className="mt-10 mb-8 max-w-2xl">
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Plan trips that fit{" "}
            <span className="bg-[linear-gradient(135deg,#4f46e5,#7c3aed)] bg-clip-text text-transparent">
              you
            </span>
            .
          </h2>
          <p className="mt-3 text-slate-500">
            Tell Atlas where you&apos;re going and what you love. It builds a
            day-by-day plan grounded in travel data, and you can refine it
            anytime.
          </p>
        </section>

        <div className="grid gap-8 lg:grid-cols-[400px_1fr]">
          <div className="lg:sticky lg:top-8 lg:self-start">
            <TripForm loading={generating} onSubmit={generate} />
          </div>

          <div className="space-y-4">
            {error && (
              <div className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700 ring-1 ring-rose-100">
                {error}
              </div>
            )}

            {generating && <Skeleton />}

            {!generating && itinerary && (
              <>
                <ItineraryView text={itinerary} />
                <ReviseBox loading={revising} onRevise={revise} />
                <SourceList sources={sources} />
              </>
            )}

            {!generating && !itinerary && !error && (
              <div className="flex h-full min-h-[320px] flex-col items-center justify-center rounded-3xl border-2 border-dashed border-slate-200 p-8 text-center">
                <div className="mb-3 text-4xl">🧭</div>
                <p className="font-semibold text-slate-700">
                  Your itinerary will appear here
                </p>
                <p className="mt-1 text-sm text-slate-400">
                  Fill in the form and hit &ldquo;Create itinerary&rdquo;.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
