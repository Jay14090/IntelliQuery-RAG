"""
Grounding verification chain.

Checks whether a generated answer is fully supported by the retrieved
context — inspired by Self-RAG (Asai et al., 2023).
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from intelliquery.prompts.verify import VERIFY_GROUNDING_TEMPLATE


class VerifyOutput(BaseModel):
    """Structured output from the verification chain."""
    is_grounded: bool = Field(
        description="True if every claim in the answer is supported by the context."
    )
    unsupported_claims: list[str] = Field(
        default_factory=list,
        description="List of claims that lack support in the context (empty if grounded)."
    )


class VerifyChain:
    """
    Audit whether a generated answer is grounded in the provided context.

    Usage::

        chain = VerifyChain(llm)
        result = chain.run(context="...", answer="...")
        if not result.is_grounded:
            print("Unsupported:", result.unsupported_claims)
    """

    def __init__(self, llm: BaseChatModel) -> None:
        self._prompt = PromptTemplate(
            template=VERIFY_GROUNDING_TEMPLATE,
            input_variables=["context", "answer"],
        )
        self._chain = self._prompt | llm.with_structured_output(VerifyOutput)

    def run(self, context: str, answer: str) -> VerifyOutput:
        """Check grounding of an answer against context."""
        return self._chain.invoke({"context": context, "answer": answer})
