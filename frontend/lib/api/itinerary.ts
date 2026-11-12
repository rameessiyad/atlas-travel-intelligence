import { apiPost } from "./client";
import type { ItineraryResponse, TripRequest } from "@/types/trip";

export function createItinerary(trip: TripRequest) {
  return apiPost<ItineraryResponse>("/itinerary", trip);
}

export function reviseItinerary(trip: TripRequest, itinerary: string, change: string) {
  return apiPost<ItineraryResponse>("/revise", { ...trip, itinerary, change });
}