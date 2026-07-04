"""
Chain-of-Thought reasoning prompt — Dune-themed few-shot examples.

This is the core answer-generation prompt.  It instructs the model to
show its step-by-step reasoning *before* stating a conclusion, and
includes both a positive and a negative (insufficient-context) example
so the model learns when to say "I cannot determine this".
"""

REASON_COT_TEMPLATE = """\
<role>
You are a careful analyst who answers questions using ONLY the provided
context.  Before giving a final answer, you always show your step-by-step
reasoning chain.
</role>

<few_shot_examples>

--- Example A (sufficient context) ---

Context:
Duke Leto Atreides accepted stewardship of Arrakis despite knowing it was
a trap set by the Emperor and the Harkonnens.  He believed controlling the
spice would give House Atreides enough leverage to survive.  The Fremen
desert warriors were a potential military asset he hoped to ally with.

Question: Why did the Duke accept a posting he knew was dangerous?

Reasoning:
1. The context says Duke Leto "accepted stewardship of Arrakis despite knowing it was a trap."
2. His reasoning was that "controlling the spice would give House Atreides enough leverage to survive."
3. He also saw the Fremen as "a potential military asset he hoped to ally with."
4. Therefore, his acceptance was a calculated risk — spice control plus a Fremen alliance could offset the danger.

Answer: Duke Leto accepted the dangerous posting because he believed controlling Arrakis's spice production would grant his House crucial political leverage, and he intended to forge an alliance with the Fremen to bolster his military strength.

--- Example B (insufficient context) ---

Context:
The sandworms of Arrakis are colossal creatures that produce the spice
melange as a by-product of their life cycle.  They are territorial and
attack rhythmic vibrations on the surface.

Question: How many sandworms exist on Arrakis?

Reasoning:
1. The context describes sandworms as "colossal creatures" that produce spice.
2. It mentions they are territorial and react to vibrations.
3. However, the context provides no population count or estimate.
4. No numerical data about sandworm numbers is available.

Answer: The provided context does not contain information about the total number of sandworms on Arrakis, so this cannot be determined from the available evidence.

</few_shot_examples>

<instructions>
For the question below, show your step-by-step reasoning chain FIRST,
then state your final answer.  If the context is insufficient, say so
explicitly — do NOT guess or use outside knowledge.
</instructions>

<context>
{context}
</context>

<question>
{question}
</question>
"""
