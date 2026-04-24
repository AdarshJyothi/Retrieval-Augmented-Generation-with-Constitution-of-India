# pipeline/services/prompt_builder.py


def build_prompt(query: str, context_chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a Gemma-style instruction prompt.

    Args:
        query:          The user's question.
        context_chunks: List of chunk dicts from retriever.retrieve().

    Returns:
        A formatted prompt string ready for the LLM.
    """
    context_str = _format_context(context_chunks)

    prompt = (
        "<start_of_turn>user\n"
        "You are a constitutional law expert on the Indian Constitution.\n"
        "Answer the question below using ONLY the provided context.\n"
        "If the answer is not in the context, say 'I don't have enough information'.\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {query}\n"
        "<end_of_turn>\n"
        "<start_of_turn>model\n"
    )
    return prompt


def _format_context(chunks: list[dict]) -> str:
    """
    Convert a list of chunk dicts into a numbered,
    labelled context string for the prompt.

    Args:
        chunks: List of chunk dicts from retriever.retrieve().

    Returns:
        A formatted multi-line string.
    """
    parts = []

    for i, chunk in enumerate(chunks, 1):
        section = chunk.get("section", "Unknown")
        chapter = chunk.get("chapter", "")

        # Build label e.g. "Part III — CHAPTER I" or just "Preamble"
        if chapter and str(chapter) != "0" and str(chapter) != "nan":
            label = f"{section} — {chapter}"
        else:
            label = section

        parts.append(f"[{i}] ({label})\n{chunk['text']}")

    return "\n\n".join(parts)