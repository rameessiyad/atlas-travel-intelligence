export type Pace = "Relaxed" | "Balanced" | "Busy";

export interface TripRequest {
  destination: string;
  days: number;
  budget: string;
  interests: string;
  pace: Pace;
  extra: string;
}

export interface Source {
  id: string;
  place: string;
  source: string;
}

export interface ItineraryResponse {
  itinerary: string;
  sources: Source[];
}