from transformers import AutoTokenizer
TOK = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-mpnet-base-dot-v1")

def count_tokens(text: str) -> int:
    # add_special_tokens ensures model-realistic length
    return len(TOK.encode(text, add_special_tokens=True))