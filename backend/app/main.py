import json
import math
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
DATA_PATH = BASE_DIR / "data" / "documents.json"

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

app = FastAPI(title="InsightSearch API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=4, ge=1, le=8)

class Source(BaseModel):
    id: str
    title: str
    category: str
    snippet: str
    score: float

class SearchResponse(BaseModel):
    answer: str
    sources: list[Source]
    query: str
    took_ms: int

def load_documents() -> list[dict[str, Any]]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

DOCUMENTS = load_documents()

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)

def get_client() -> genai.Client:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=key)


GEMINI_CLIENT = get_client()

def embed_texts(texts: list[str]) -> list[list[float]]:
    response = GEMINI_CLIENT.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    return [item.values for item in response.embeddings]

def embed_query(query: str) -> list[float]:
    response = GEMINI_CLIENT.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return response.embeddings[0].values

# The small dataset is embedded at startup. This keeps the MVP simple and avoids
# a database or vector store while still demonstrating real semantic retrieval.
DOCUMENT_EMBEDDINGS: list[list[float]] = []

@app.on_event("startup")
def warm_embeddings() -> None:
    global DOCUMENT_EMBEDDINGS
    if os.getenv("GEMINI_API_KEY"):
        try:
            DOCUMENT_EMBEDDINGS = embed_texts(
                [f"{doc['title']}\n{doc['content']}" for doc in DOCUMENTS]
            )
        except Exception as exc:
            print(f"Embedding warmup skipped: {exc}")

def retrieve(query: str, top_k: int) -> list[tuple[dict[str, Any], float]]:
    global DOCUMENT_EMBEDDINGS
    if not DOCUMENT_EMBEDDINGS:
        DOCUMENT_EMBEDDINGS = embed_texts(
            [f"{doc['title']}\n{doc['content']}" for doc in DOCUMENTS]
        )
    query_embedding = embed_query(query)
    scored = [
        (doc, cosine_similarity(query_embedding, embedding))
        for doc, embedding in zip(DOCUMENTS, DOCUMENT_EMBEDDINGS)
    ]
    return sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]

def generate_answer(query: str, retrieved: list[tuple[dict[str, Any], float]]) -> str:
    context = "\n\n".join(
        f"[{doc['id']}] {doc['title']}\n{doc['content']}" for doc, _ in retrieved
    )
    prompt = f"""You are InsightSearch, a precise internal knowledge assistant.
Answer the user's question using ONLY the provided documents.
If the documents do not contain enough information, say that clearly.
Do not invent policies, dates, names, or procedures.
Cite supporting document IDs inline like [DOC-01].

Question:
{query}

Documents:
{context}
"""
    response = GEMINI_CLIENT.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text.strip() if response.text else "No grounded answer was generated."

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "documents": str(len(DOCUMENTS))}

@app.post("/api/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    started = time.perf_counter()
    try:
        retrieved = retrieve(request.query, request.top_k)
        answer = generate_answer(request.query, retrieved)
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Search failed: {exc}")
        raise HTTPException(status_code=502, detail="AI search failed. Check the Gemini API configuration.") from exc

    sources = [
        Source(
            id=doc["id"],
            title=doc["title"],
            category=doc["category"],
            snippet=doc["content"][:220] + ("..." if len(doc["content"]) > 220 else ""),
            score=round(max(0.0, min(1.0, score)), 4),
        )
        for doc, score in retrieved
    ]
    took_ms = int((time.perf_counter() - started) * 1000)
    return SearchResponse(
        answer=answer,
        sources=sources,
        query=request.query,
        took_ms=took_ms,
    )
