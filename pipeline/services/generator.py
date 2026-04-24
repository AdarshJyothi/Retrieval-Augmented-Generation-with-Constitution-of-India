# pipeline/services/generator.py

import torch
from pipeline.core.resources import get_resources
from pipeline.config import settings


def generate(prompt: str) -> str:
    """
    Run the LLM on a formatted prompt and return the generated answer.

    Args:
        prompt: The fully formatted prompt string from prompt_builder.

    Returns:
        The LLM's answer as a plain string.
    """
    resources = get_resources()

    # Step 1: Tokenize the prompt into input IDs
    inputs = resources.tokenizer(
        prompt,
        return_tensors="pt"
    ).to(resources.embeddings.device)

    # Step 2: Generate output token IDs
    with torch.no_grad():
        output_ids = resources.llm.generate(
            **inputs,
            max_new_tokens=settings.MAX_NEW_TOKENS,
            temperature=settings.TEMPERATURE,
            do_sample=settings.TEMPERATURE > 0,
            pad_token_id=resources.tokenizer.eos_token_id,
        )

    # Step 3: Slice off the input tokens — keep only the newly generated ones
    input_length = inputs["input_ids"].shape[-1]
    new_tokens = output_ids[0][input_length:]

    # Step 4: Decode tokens back into a readable string
    answer = resources.tokenizer.decode(
        new_tokens,
        skip_special_tokens=True
    ).strip()

    return answer