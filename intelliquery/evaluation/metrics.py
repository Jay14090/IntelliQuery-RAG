"""
Ragas-based evaluation of agent responses.

Wraps the Ragas library to compute standard RAG quality metrics:
answer correctness, faithfulness, relevancy, context recall, and
answer similarity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class EvaluationResult:
    """Container for evaluation metric scores (0.0 – 1.0)."""
    answer_correctness: Optional[float] = None
    faithfulness: Optional[float] = None
    answer_relevancy: Optional[float] = None
    context_recall: Optional[float] = None
    answer_similarity: Optional[float] = None

    def summary(self) -> str:
        """Pretty-print the scores."""
        lines = []
        for field_name in [
            "answer_correctness",
            "faithfulness",
            "answer_relevancy",
            "context_recall",
            "answer_similarity",
        ]:
            val = getattr(self, field_name)
            display = f"{val:.3f}" if val is not None else "n/a"
            label = field_name.replace("_", " ").title()
            lines.append(f"  {label}: {display}")
        return "\n".join(lines)


def evaluate_response(
    question: str,
    generated_answer: str,
    ground_truth: str,
    contexts: list[str],
) -> EvaluationResult:
    """
    Run Ragas evaluation on a single QA pair.

    Parameters
    ----------
    question : str
        The user's original question.
    generated_answer : str
        The agent's generated answer.
    ground_truth : str
        The expected correct answer (for correctness / similarity).
    contexts : list[str]
        Retrieved context passages used to generate the answer.

    Returns
    -------
    EvaluationResult
        Dataclass with metric scores.
    """
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_correctness,
            answer_relevancy,
            answer_similarity,
            context_recall,
            faithfulness,
        )

        eval_dataset = Dataset.from_dict({
            "question": [question],
            "answer": [generated_answer],
            "ground_truth": [ground_truth],
            "contexts": [contexts],
        })

        results = evaluate(
            eval_dataset,
            metrics=[
                answer_correctness,
                faithfulness,
                answer_relevancy,
                context_recall,
                answer_similarity,
            ],
        )

        return EvaluationResult(
            answer_correctness=results.get("answer_correctness"),
            faithfulness=results.get("faithfulness"),
            answer_relevancy=results.get("answer_relevancy"),
            context_recall=results.get("context_recall"),
            answer_similarity=results.get("answer_similarity"),
        )

    except ImportError:
        print("⚠️  ragas or datasets not installed — skipping evaluation.")
        return EvaluationResult()
    except Exception as exc:
        print(f"⚠️  Evaluation failed: {exc}")
        return EvaluationResult()
