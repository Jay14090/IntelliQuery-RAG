"""
Plan generation chain.

Takes an anonymised question and produces a structured step-by-step plan
of RETRIEVE and REASON actions.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from intelliquery.prompts.plan import PLAN_TEMPLATE


class PlanStep(BaseModel):
    """A single step in the execution plan."""
    step: int = Field(description="1-indexed step number.")
    action: Literal["RETRIEVE", "REASON"] = Field(
        description="Whether this step retrieves information or reasons over existing context."
    )
    description: str = Field(description="What this step should accomplish.")


class PlanOutput(BaseModel):
    """Full plan produced by the planner."""
    steps: list[PlanStep] = Field(description="Ordered list of plan steps.")


class PlanChain:
    """
    Generate a research plan from an anonymised question.

    Usage::

        chain = PlanChain(llm)
        plan = chain.run("Why did PERSON_1 go to LOCATION_1?")
        for step in plan.steps:
            print(step.action, step.description)
    """

    def __init__(self, llm: BaseChatModel) -> None:
        self._prompt = PromptTemplate(
            template=PLAN_TEMPLATE,
            input_variables=["anonymized_question"],
        )
        self._chain = self._prompt | llm.with_structured_output(PlanOutput)

    def run(self, anonymized_question: str) -> PlanOutput:
        """Generate an execution plan."""
        return self._chain.invoke({"anonymized_question": anonymized_question})
