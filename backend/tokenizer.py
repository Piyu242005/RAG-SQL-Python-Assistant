"""Utility for token counting using tiktoken."""
import logging
import tiktoken
from typing import Optional

logger = logging.getLogger("tokenizer")

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """
    Count tokens in a text string using tiktoken.
    Defaults to cl100k_base (OpenAI/GPT-4 encoding), which is a good
    heuristic for most modern LLMs including Llama 3 if the exact
    tokenizer isn't available.
    """
    try:
        # If text is empty or None
        if not text:
            return 0
            
        # Try to get encoding for the specific model or use a base one
        try:
            encoding = tiktoken.get_encoding(model)
        except ValueError:
            encoding = tiktoken.get_encoding("cl100k_base")
            
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Token counting failed: {e}. Falling back to char/3 heuristic.")
        # Fallback to the character-based heuristic (roughly 3-4 characters per token)
        return len(text) // 3
