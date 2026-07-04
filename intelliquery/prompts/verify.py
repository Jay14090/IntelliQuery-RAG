"""
Prompt template for grounding verification.

Inspired by Self-RAG (Asai et al., 2023) — checks whether a generated
answer is fully supported by the retrieved context, flagging any
unsupported claims.
"""

VERIFY_GROUNDING_TEMPLATE = """\
<role>
You are a grounding auditor.  You must determine whether EVERY factual
claim in the generated answer is supported by the provided context.
</role>

<context>
{context}
</context>

<generated_answer>
{answer}
</generated_answer>

<instructions>
1. List each factual claim made in the answer.
2. For each claim, note whether the context explicitly supports it.
3. If ALL claims are supported, set ``is_grounded`` to true.
4. If ANY claim lacks support, set ``is_grounded`` to false and list the
   unsupported claims in ``unsupported_claims``.
</instructions>

Respond with the structured output only.
"""
