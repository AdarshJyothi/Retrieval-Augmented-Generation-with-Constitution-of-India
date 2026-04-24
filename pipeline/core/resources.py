# pipeline/core/resources.py
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer

from pipeline.config import settings


@dataclass
class AppResources:
    embeddings: torch.Tensor
    chunks: list[dict]
    embed_model: SentenceTransformer
    llm: AutoModelForCausalLM
    tokenizer: AutoTokenizer


_resources: Optional[AppResources] = None


def _parse_embedding(value) -> list[float]:
    """
    Parse an embedding column value loaded from CSV into a list[float].
    Handles stringified Python lists.
    """
    if isinstance(value, list):
        return [float(x) for x in value]

    if isinstance(value, str):
        return [float(x) for x in ast.literal_eval(value)]

    raise ValueError("Unsupported embedding format in CSV.")


def load_resources() -> AppResources:
    """
    Load and cache all heavyweight resources once.
    Safe to call multiple times; returns cached resources after first load.
    """
    global _resources

    if _resources is not None:
        return _resources

    df = pd.read_csv(settings.CSV_PATH)
    df["embedding"] = df["embedding"].apply(_parse_embedding)

    chunks = df.to_dict(orient="records")
    embeddings = torch.tensor(
        [row["embedding"] for row in chunks],
        dtype=torch.float32
    ).to(settings.DEVICE)

    embed_model = SentenceTransformer(settings.EMBED_MODEL_NAME)
    embed_model.to(settings.DEVICE)

    tokenizer = AutoTokenizer.from_pretrained(settings.LLM_NAME)

    model_kwargs = {"device_map": "auto"}

    if settings.USE_QUANTIZATION:
        from transformers import BitsAndBytesConfig
        model_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
    else:
        model_kwargs["torch_dtype"] = torch.float16

    llm = AutoModelForCausalLM.from_pretrained(
        settings.LLM_NAME,
        **model_kwargs
    )
    llm.eval()

    _resources = AppResources(
        embeddings=embeddings,
        chunks=chunks,
        embed_model=embed_model,
        llm=llm,
        tokenizer=tokenizer,
    )
    return _resources


def get_resources() -> AppResources:
    """
    Return already loaded resources.
    Raises an error if startup loading was not run.
    """
    if _resources is None:
        raise RuntimeError(
            "Resources not loaded. Call load_resources() at application startup."
        )
    return _resources