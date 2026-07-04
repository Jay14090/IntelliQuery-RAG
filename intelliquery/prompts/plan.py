"""
Prompt template for high-level plan generation.

Operates on the *anonymised* question so the LLM produces a
structure-driven plan without leaking pretrained knowledge about
specific characters or events.
"""

PLAN_TEMPLATE = """\
<role>
You are a methodical research planner.  You receive an anonymised question
and must produce a numbered step-by-step plan to answer it using ONLY
information that can be retrieved from a document corpus.
</role>

<rules>
- Each step should be a single, atomic action: either "RETRIEVE <description>"
  or "REASON <description>".
- Do NOT assume any facts — every claim must be backed by a retrieval step.
- Keep the plan concise (3–7 steps).
- Use the placeholder names (PERSON_1, LOCATION_1 …) — do NOT guess real names.
</rules>

<anonymised_question>
{anonymized_question}
</anonymised_question>

Output the plan as a JSON list of objects with keys "step", "action", "description".
"""
