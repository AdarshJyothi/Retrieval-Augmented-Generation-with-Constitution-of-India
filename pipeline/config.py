# pipeline/config.py

import torch
from dataclasses import dataclass


@dataclass
class Settings:
    # ── Data ──────────────────────────────────────────────
    CSV_PATH: str = "constitution_embeddings.csv"

    # ── Models ────────────────────────────────────────────
    EMBED_MODEL_NAME: str = "multi-qa-mpnet-base-dot-v1"
    LLM_NAME: str         = "google/gemma-2b-it"

    # ── Retrieval ─────────────────────────────────────────
    TOP_K: int            = 10

    # ── Generation ────────────────────────────────────────
    MAX_NEW_TOKENS: int   = 1024
    TEMPERATURE: float    = 0.3

    # ── Hardware ──────────────────────────────────────────
    DEVICE: str           = "cuda" if torch.cuda.is_available() else "cpu"
    USE_QUANTIZATION: bool = torch.cuda.is_available()  # only quantize if GPU present


settings = Settings()