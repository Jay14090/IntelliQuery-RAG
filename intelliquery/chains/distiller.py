"""
Context distillation chain.

Filters retrieved documents down to only the parts relevant to the
current query — reducing noise before the reasoning step.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from intelliquery.prompts.distill import DISTILL_TEMPLATE


class DistillOutput(BaseModel):
    """Structured output from the distillation chain."""
    relevant_content: str = Field(
        description="Filtered text containing only query-relevant information."
    )


class DistillChain:
    """
    Distill raw retrieved context into lean, relevant content.

    Usage::

        chain = DistillChain(llm)
        result = chain.run(query="...", documents="...")
        print(result.relevant_content)
    """

    def __init__(self, llm: BaseChatModel) -> None:
        self._prompt = PromptTemplate(
            template=DISTILL_TEMPLATE,
            input_variables=["query", "documents"],
        )
        self._chain = self._prompt | llm.with_structured_output(DistillOutput)

    def run(self, query: str, documents: str) -> DistillOutput:
        """Filter irrelevant content from retrieved documents."""
        return self._chain.invoke({"query": query, "documents": documents})
