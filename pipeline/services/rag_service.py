# pipeline/services/rag_service.py

from pipeline.config import settings
from pipeline.services.retriever import retrieve
from pipeline.services.prompt_builder import build_prompt
from pipeline.services.generator import generate


def run_rag(query: str, top_k: int | None = None) -> dict:
    """
    Full RAG pipeline: retrieve → build prompt → generate.

    Args:
        query:  The user's question string.
        top_k:  Number of chunks to retrieve. Defaults to settings.TOP_K.

    Returns:
        Dict with keys:
            - answer  (str):        The LLM's generated answer.
            - sources (list[dict]): The retrieved chunks used as context.
    """
    k = top_k or settings.TOP_K

    # Step 1: Retrieve top-k relevant chunks
    chunks = retrieve(query, top_k=k)

    # Step 2: Format chunks + query into a prompt
    prompt = build_prompt(query, chunks)

    # Step 3: Generate answer from the prompt
    answer = generate(prompt)

    return {
        "answer": answer,
        "sources": chunks,
    }