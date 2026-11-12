import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

DB_DIR = "chroma_db"
COLLECTION = "travel_places"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_collection = None

def _get_collection():
    global _collection
    if _collection is None:
        ef = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=DB_DIR)
        _collection = client.get_or_create_collection(name=COLLECTION, embedding_function=ef)
    return _collection

def retrieve_travel_notes(question: str, limit: int = 4):
    col = _get_collection()
    if col.count() == 0:
        return []
    res = col.query(query_texts=[question], n_results=min(limit, col.count()))
    notes = []
    for doc_id, doc, meta, dist in zip(
        res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        notes.append({
            "id": doc_id,
            "text": doc,
            "place_name": meta.get("place_name", ""),
            "city": meta.get("city", ""),
            "country": meta.get("country", ""),
            "source": meta.get("source", ""),
            "distance": round(dist, 4),
        })
    return notes