"""
Text cleaning and normalisation utilities.

These are intentionally *pure functions* with no LLM calls so they can be
unit-tested in isolation.
"""

from __future__ import annotations

import re

import tiktoken


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count the number of tokens ``text`` encodes to under the given model's
    tokenizer.

    Parameters
    ----------
    text : str
        Raw text to tokenize.
    model : str
        Model whose tokenizer to use (any tiktoken-supported name).

    Returns
    -------
    int
        Token count.
    """
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))


def normalize_whitespace(text: str) -> str:
    """
    Collapse runs of tabs and spaces into single spaces while preserving
    newline structure.
    """
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def strip_redundant_newlines(text: str) -> str:
    """Collapse two-or-more consecutive newlines into exactly one."""
    return re.sub(r"\n{2,}", "\n", text)


def sanitize_quotes(text: str) -> str:
    """
    Escape unbalanced or special quote characters that may break downstream
    prompt templates or JSON serialisation.
    """
    text = text.replace('"', '\\"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")  # smart single
    text = text.replace("\u201c", '"').replace("\u201d", '"')  # smart double
    return text


def clean_document_text(text: str) -> str:
    """
    One-shot pipeline: normalise whitespace → strip redundant newlines →
    sanitize quotes.
    """
    text = normalize_whitespace(text)
    text = strip_redundant_newlines(text)
    text = sanitize_quotes(text)
    return text
