from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import retrieve_travel_notes
from model import answer_with_qwen, revise_with_qwen

app = FastAPI(title="Atlas Travel AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripRequest(BaseModel):
    destination: str
    days: int = 3
    budget: str = ""
    interests: str = ""
    pace: str = "Balanced"
    extra: str = ""


class ReviseRequest(TripRequest):
    itinerary: str
    change: str


def build_request(req: TripRequest) -> str:
    return (
        f"Create a {req.days}-day itinerary for {req.destination}. "
        f"Budget: {req.budget or 'not specified'}. "
        f"Interests: {req.interests or 'not specified'}. "
        f"Pace: {req.pace}. Extra preferences: {req.extra or 'none'}."
    )


def source_list(notes):
    return [
        {"id": n["id"], "place": n["place_name"], "source": n["source"]}
        for n in notes
    ]


@app.get("/health")
def health():
    return {"status": "ok", "app": "Atlas"}


@app.get("/retrieve")
def retrieve(q: str, limit: int = 4):
    return {"query": q, "results": retrieve_travel_notes(q, limit)}


@app.post("/itinerary")
def itinerary(req: TripRequest):
    notes = retrieve_travel_notes(f"{req.destination} {req.interests}", limit=4)
    answer = answer_with_qwen(build_request(req), notes)
    return {"itinerary": answer, "sources": source_list(notes)}


@app.post("/revise")
def revise(req: ReviseRequest):
    notes = retrieve_travel_notes(f"{req.destination} {req.interests}", limit=4)
    answer = revise_with_qwen(build_request(req), req.itinerary, req.change, notes)
    return {"itinerary": answer, "sources": source_list(notes)}