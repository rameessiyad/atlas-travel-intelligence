from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag import retrieve_travel_notes

app = FastAPI(title="Atlas Travel AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "app": "Atlas"}

@app.get("/retrieve")
def retrieve(q: str, limit: int = 4):
    return {"query": q, "results": retrieve_travel_notes(q, limit)}