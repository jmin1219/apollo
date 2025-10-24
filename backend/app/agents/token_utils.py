from functools import lru_cache

@lru_cache(maxsize=16)
def _get_encoding_cached(model_name: str):
    import tiktoken
    return tiktoken.encoding_for_model(model_name)

def ensure_tiktoken_available() -> None:
  """Ensure tiktoken can be imported, otherwise raise an informative error."""
  try:
    import tiktoken
  except ImportError as e:
    raise ImportError(
        "The 'tiktoken' library is required for token counting functionality. "
        "Please install it using 'pip install tiktoken'."
    ) from e

def get_tokenizer(model_name: str):
    """Return a tiktoken encoding object for the given model name. Raise an error if unsupported."""
    ensure_tiktoken_available()
    import tiktoken

    try:
        encoding = _get_encoding_cached(model_name)
    except KeyError:
        raise ValueError(
            f"Model '{model_name}' is not supported for token counting. "
            "Please use a supported model."
        )
    return encoding

def count_tokens(text: str, model_name: str) -> int:
    """Count the number of tokens in the given text for the specified model."""
    tokenizer = get_tokenizer(model_name)  # 
    tokens = tokenizer.encode(text)
    return len(tokens)


