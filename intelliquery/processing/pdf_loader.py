"""
PDF loading and chapter-splitting logic.

Designed around the structure of Frank Herbert's *Dune*, which is divided
into three named **Books** (each containing multiple sections).  The
``chapter_split_pattern`` in ``config.yaml`` can be adjusted for other
PDF structures.
"""

from __future__ import annotations

import re
from pathlib import Path

import PyPDF2
from langchain_core.documents import Document

from intelliquery.processing.text_cleaner import clean_document_text


def extract_full_text(pdf_path: str | Path) -> str:
    """
    Read every page of a PDF and return the concatenated raw text.

    Parameters
    ----------
    pdf_path : path-like
        Filesystem path to the PDF file.

    Returns
    -------
    str
        The full extracted text.
    """
    pdf_path = Path(pdf_path)
    with open(pdf_path, "rb") as fh:
        reader = PyPDF2.PdfReader(fh)
        pages_text = [page.extract_text() or "" for page in reader.pages]
    return " ".join(pages_text)


def split_into_sections(
    raw_text: str,
    pattern: str | None = None,
) -> list[Document]:
    """
    Split the full book text into ``Document`` objects, one per section.

    The default pattern targets Dune's structure
    (``BOOK ONE``, ``BOOK TWO``, ``BOOK THREE``).  Override via
    ``config.yaml → processing.chapter_split_pattern`` for other books.

    Parameters
    ----------
    raw_text : str
        Full book text as a single string.
    pattern : str, optional
        Regex with a capturing group around section headers.

    Returns
    -------
    list[Document]
        Each document carries ``page_content`` (cleaned section text) and
        ``metadata`` with a ``section`` index.
    """
    if pattern is None:
        # Dune default: match "BOOK ONE", "BOOK TWO", etc. as delimiters
        pattern = r"(BOOK\s+(?:ONE|TWO|THREE)[^\n]*)"

    parts = re.split(pattern, raw_text, flags=re.IGNORECASE)

    documents: list[Document] = []
    section_idx = 1

    # re.split with a capturing group interleaves headers and bodies:
    #   [preamble, header1, body1, header2, body2, ...]
    # We skip the preamble (index 0) if it's just front-matter.
    i = 1  # start after preamble
    while i < len(parts) - 1:
        header = parts[i].strip()
        body = parts[i + 1].strip() if (i + 1) < len(parts) else ""
        full_section = f"{header}\n{body}"
        cleaned = clean_document_text(full_section)

        if len(cleaned) > 50:  # skip trivially short fragments
            documents.append(
                Document(
                    page_content=cleaned,
                    metadata={"section": section_idx, "header": header},
                )
            )
            section_idx += 1
        i += 2

    # If regex matched nothing, return the whole text as one document
    if not documents:
        documents.append(
            Document(
                page_content=clean_document_text(raw_text),
                metadata={"section": 1, "header": "Full Text"},
            )
        )

    return documents


def load_and_split_pdf(
    pdf_path: str | Path,
    pattern: str | None = None,
) -> list[Document]:
    """
    End-to-end helper: extract text from PDF then split into sections.

    Parameters
    ----------
    pdf_path : path-like
        Path to the PDF.
    pattern : str, optional
        Section-split regex (forwarded to :func:`split_into_sections`).

    Returns
    -------
    list[Document]
    """
    raw = extract_full_text(pdf_path)
    return split_into_sections(raw, pattern=pattern)
