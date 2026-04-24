# pipeline/services/retriever.py

import torch
from pipeline.core.resources import get_resources


def retrieve(query: str, top_k: int) -> list[dict]:
    """
    Embed the query and return the top-k most relevant chunks.

    Args:
        query:  The user's question string.
        top_k:  Number of chunks to return.

    Returns:
        List of chunk dicts with keys: text, section, chapter, token_count, score.
    """
    resources = get_resources()

    # Step 1: Embed + normalize the query
    query_vec = resources.embed_model.encode(
        query,
        convert_to_tensor=True,
        normalize_embeddings=True,
    ).to(resources.embeddings.device)

    # Step 2: Dot product similarity (cosine sim since both are normalized)
    scores = torch.mv(resources.embeddings, query_vec)   # shape: (N,)

    # Step 3: Get top-k indices
    top_indices = torch.topk(scores, k=top_k).indices.tolist()

    # Step 4: Build result list, stripping the stored embedding column
    results = []
    for idx in top_indices:
        chunk = {
            k: v for k, v in resources.chunks[idx].items()
            if k != "embedding"
        }
        chunk["score"] = round(float(scores[idx]), 4)
        results.append(chunk)

    return results