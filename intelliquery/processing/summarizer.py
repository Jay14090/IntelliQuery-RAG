"""
Chapter / section summarisation via LLM.

Produces condensed summaries of each section that are later encoded into a
dedicated vector store for high-level retrieval.
"""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel

_SUMMARIZE_TEMPLATE = """\
<task>
You are a meticulous literary analyst.  Produce a detailed yet concise summary
of the following book section.  Capture the key events, character motivations,
and any world-building details that would help answer complex questions later.
</task>

<section_header>{header}</section_header>

<section_text>
{text}
</section_text>

<instructions>
- Write 3–5 paragraphs.
- Preserve character names and important terminology exactly.
- Do NOT add speculation — only information explicitly stated in the text.
</instructions>
"""

_SUMMARIZE_PROMPT = PromptTemplate(
    template=_SUMMARIZE_TEMPLATE,
    input_variables=["header", "text"],
)


def summarize_section(section: Document, llm: BaseChatModel) -> Document:
    """
    Generate an LLM summary for a single section ``Document``.

    Returns a *new* ``Document`` whose ``page_content`` is the summary and
    whose ``metadata`` inherits the original section number.
    """
    chain = _SUMMARIZE_PROMPT | llm
    result = chain.invoke({
        "header": section.metadata.get("header", ""),
        "text": section.page_content,
    })
    summary_text = result.content if hasattr(result, "content") else str(result)
    return Document(
        page_content=summary_text,
        metadata={**section.metadata, "type": "summary"},
    )


def summarize_all_sections(
    sections: list[Document],
    llm: BaseChatModel,
    *,
    verbose: bool = False,
) -> list[Document]:
    """
    Summarize every section in ``sections``.

    Parameters
    ----------
    sections : list[Document]
        Output of :func:`~intelliquery.processing.pdf_loader.load_and_split_pdf`.
    llm : BaseChatModel
        Chat model to use for summarisation.
    verbose : bool
        Print progress to stdout.

    Returns
    -------
    list[Document]
        One summary document per input section.
    """
    summaries: list[Document] = []
    for idx, sec in enumerate(sections, start=1):
        if verbose:
            print(f"  ⏳ Summarising section {idx}/{len(sections)}: "
                  f"{sec.metadata.get('header', '?')}")
        summaries.append(summarize_section(sec, llm))
    return summaries
