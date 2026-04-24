# utils.py

from transformers import AutoTokenizer
# load tokenizer once at module level
TOK = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-mpnet-base-dot-v1")

def count_tokens(text: str) -> int:
    """Return number of tokens in text using the chosen tokenizer."""
    return len(TOK.encode(text, add_special_tokens=True))
