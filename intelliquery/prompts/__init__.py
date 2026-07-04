"""Versioned prompt templates for every chain in the pipeline."""

from intelliquery.prompts.anonymize import ANONYMIZE_TEMPLATE
from intelliquery.prompts.plan import PLAN_TEMPLATE
from intelliquery.prompts.distill import DISTILL_TEMPLATE
from intelliquery.prompts.reason import REASON_COT_TEMPLATE
from intelliquery.prompts.verify import VERIFY_GROUNDING_TEMPLATE

__all__ = [
    "ANONYMIZE_TEMPLATE",
    "PLAN_TEMPLATE",
    "DISTILL_TEMPLATE",
    "REASON_COT_TEMPLATE",
    "VERIFY_GROUNDING_TEMPLATE",
]
