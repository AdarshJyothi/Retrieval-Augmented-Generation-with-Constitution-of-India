# pipeline/app.py

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pipeline.core.resources import load_resources
from pipeline.services.rag_service import run_rag


# ─────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────

class AskRequest(BaseModel):
    query: str
    top_k: int | None = None


class SourceChunk(BaseModel):
    text: str
    section: str
    chapter: str | None = None
    token_count: int
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


# ─────────────────────────────────────────────
# Lifespan — load models once at startup
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the server starts.
    Loads all heavy resources before the first request is served.
    """
    load_resources()
    yield
    # anything after yield runs on shutdown (cleanup if needed)


# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────

app = FastAPI(
    title="Indian Constitution RAG API",
    description="Ask questions about the Indian Constitution.",
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/health")
def health():
    """Sanity check — confirms the server is running."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """
    Takes a query, runs the full RAG pipeline,
    and returns the answer + source chunks.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    result = run_rag(query=request.query, top_k=request.top_k)

    return AskResponse(
        answer=result["answer"],
        sources=result["sources"],
    )