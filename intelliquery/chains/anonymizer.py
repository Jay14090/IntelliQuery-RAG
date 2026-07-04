"""
Question anonymisation chain.

Replaces named entities with placeholders and returns both the
anonymised question and the entity mapping for later de-anonymisation.
"""

from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from intelliquery.prompts.anonymize import ANONYMIZE_TEMPLATE


class EntityMapping(BaseModel):
    placeholder: str = Field(description="e.g. PERSON_1")
    original_entity: str = Field(description="The real entity name.")

class AnonymizeLLMOutput(BaseModel):
    anonymized_question: str = Field(
        description="The question with all named entities replaced by placeholders."
    )
    entity_mappings: list[EntityMapping] = Field(
        description="List of entity mappings."
    )

class AnonymizeOutput(BaseModel):
    """Structured output from the anonymisation chain."""
    anonymized_question: str
    entity_map: dict[str, str]


class AnonymizeChain:
    """
    Wrap the anonymise prompt + LLM into a callable chain.

    Usage::

        chain = AnonymizeChain(llm)
        result = chain.run("Why did Paul go to Arrakis?")
        print(result.anonymized_question)
        print(result.entity_map)
    """

    def __init__(self, llm: BaseChatModel) -> None:
        self._prompt = PromptTemplate(
            template=ANONYMIZE_TEMPLATE,
            input_variables=["question"],
        )
        self._chain = self._prompt | llm.with_structured_output(AnonymizeLLMOutput)

    def run(self, question: str) -> AnonymizeOutput:
        """Execute the anonymisation chain on a raw question."""
        llm_result = self._chain.invoke({"question": question})
        mapping = {m.placeholder: m.original_entity for m in llm_result.entity_mappings}
        return AnonymizeOutput(
            anonymized_question=llm_result.anonymized_question,
            entity_map=mapping,
        )
