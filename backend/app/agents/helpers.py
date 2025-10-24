"""Token utilities for agents (tiktoken wrappers).

Small, testable helpers to count tokens and trim conversation history by a
target token budget. These are intentionally simple so you can iterate on the
overhead heuristics later.
"""
from functools import lru_cache
from typing import List, Tuple

import tiktoken


@lru_cache(maxsize=4)
def _get_encoder(encoding_name: str = "cl100k_base"):
    return tiktoken.get_encoding(encoding_name)


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Return the token count for a single string.

    Notes:
    - Use `encoding_for_model(model_name)` if you need model-specific encodings.
    - Keep this cheap and pure for easy unit testing.
    """
    if not text:
        return 0
    enc = _get_encoder(encoding_name)
    return len(enc.encode(text))


def trim_history_by_tokens(
    history: List[str], max_tokens: int, encoding_name: str = "cl100k_base", per_message_overhead: int = 8
) -> Tuple[List[str], int]:
    """Trim conversation history (oldest-first list) so kept messages token
    count <= max_tokens, keeping the most recent messages.

    Returns (kept_history_oldest_first, kept_tokens)
    """
    if max_tokens <= 0:
        return [], 0

    kept: List[str] = []
    total = 0

    # Iterate newest -> oldest so we preferentially keep recent messages
    for msg in reversed(history):
        tok = count_tokens(msg, encoding_name) + per_message_overhead
        if total + tok > max_tokens:
            break
        kept.append(msg)
        total += tok

    kept.reverse()
    return kept, total
