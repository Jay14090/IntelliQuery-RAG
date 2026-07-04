"""
Prompt template for context distillation.

Takes raw retrieved documents and a query, then filters out all
non-relevant noise — producing a lean, focused context for downstream
reasoning.
"""

DISTILL_TEMPLATE = """\
<role>
You are a precision text filter.  Your only job is to remove irrelevant
information from retrieved documents while preserving every fact that
relates to the query.
</role>

<query>
{query}
</query>

<retrieved_documents>
{documents}
</retrieved_documents>

<rules>
- Remove sentences, clauses, or fragments that do NOT contribute meaningful
  information toward answering the query.
- You may trim within a sentence if only part of it is relevant.
- NEVER add, infer, or fabricate information beyond what appears in the
  retrieved documents.
- Preserve exact names, numbers, and quoted dialogue.
</rules>

Output the filtered, relevant content only.
"""
