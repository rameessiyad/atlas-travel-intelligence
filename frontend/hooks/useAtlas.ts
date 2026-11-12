"use client";

import { useState } from "react";
import { createItinerary, reviseItinerary } from "@/lib/api/itinerary";
import type { Source, TripRequest } from "@/types/trip";

type Status = "idle" | "generating" | "revising";

export function useAtlas() {
  const [trip, setTrip] = useState<TripRequest | null>(null);
  const [itinerary, setItinerary] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");

  async function run(next: Status, call: () => Promise<{ itinerary: string; sources: Source[] }>) {
    setStatus(next);
    setError("");
    try {
      const data = await call();
      setItinerary(data.itinerary);
      setSources(data.sources);
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      return false;
    } finally {
      setStatus("idle");
    }
  }

  const generate = (t: TripRequest) => {
    setTrip(t);
    return run("generating", () => createItinerary(t));
  };

  const revise = (change: string) =>
    trip ? run("revising", () => reviseItinerary(trip, itinerary, change)) : Promise.resolve(false);

  return { itinerary, sources, status, error, generate, revise };
}