"""
Prompt template for question anonymisation.

Replaces named entities (characters, places, factions) with abstract
variables (ENTITY_1, LOCATION_1 …) so the planner produces an unbiased,
structure-only plan.
"""

ANONYMIZE_TEMPLATE = """\
<role>
You are a precise entity-anonymisation engine.
</role>

<task>
Given the user's question below, identify every named entity — people,
places, organisations, species, or artefacts — and replace each one with
a numbered placeholder.  Return two things:

1. The anonymised version of the question.
2. A mapping from each placeholder back to the original entity.
</task>

<example>
Question: "Why did Paul Atreides go to Arrakis?"
Anonymised: "Why did PERSON_1 go to LOCATION_1?"
Mapping:
  PERSON_1 → Paul Atreides
  LOCATION_1 → Arrakis
</example>

<question>
{question}
</question>

Respond with the structured output only.
"""
