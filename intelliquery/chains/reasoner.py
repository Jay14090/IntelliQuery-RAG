"""
Chain-of-Thought reasoning chain.

Generates an answer by first showing step-by-step reasoning, then
stating a conclusion — strictly grounded in the provided context.
"""

from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from intelliquery.prompts.reason import REASON_COT_TEMPLATE


class ReasonOutput(BaseModel):
    """Structured output from the reasoning chain."""
    reasoning_chain: str = Field(
        description="Step-by-step reasoning process showing how the answer was derived."
    )
    answer: str = Field(
        description="Final answer to the question, grounded in context."
    )


class ReasonChain:
    """
    Answer a question using chain-of-thought reasoning over context.

    Usage::

        chain = ReasonChain(llm)
        result = chain.run(context="...", question="...")
        print(result.reasoning_chain)
        print(result.answer)
    """

    def __init__(self, llm: BaseChatModel) -> None:
        self._prompt = PromptTemplate(
            template=REASON_COT_TEMPLATE,
            input_variables=["context", "question"],
        )
        self._chain = self._prompt | llm.with_structured_output(ReasonOutput)

    def run(self, context: str, question: str) -> ReasonOutput:
        """Generate a reasoned answer from context."""
        return self._chain.invoke({"context": context, "question": question})
