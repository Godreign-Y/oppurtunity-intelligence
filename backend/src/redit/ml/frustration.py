"""Semantic frustration detection using zero-shot classification."""

from dataclasses import dataclass

from transformers import pipeline


@dataclass(frozen=True)
class FrustrationScore:
    """Semantic frustration scoring result."""

    label: str
    score: float
    frustration_detected: bool


class FrustrationAnalyzer:
    """Semantic developer frustration detector."""

    def __init__(self, frustration_threshold: float = 0.55) -> None:

        self._classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
        )

        self._threshold = frustration_threshold

        self._labels = [
            "developer frustration",
            "workflow pain",
            "tooling annoyance",
            "operational inefficiency",
            "infrastructure complexity",
            "positive discussion",
        ]

    def score(self, text: str) -> FrustrationScore:
        """Classify semantic frustration."""

        result = self._classifier(
            text,
            candidate_labels=self._labels,
            multi_label=False,
        )

        top_label = str(result["labels"][0])
        top_score = float(result["scores"][0])

        frustration_labels = {
            "developer frustration",
            "workflow pain",
            "tooling annoyance",
            "operational inefficiency",
            "infrastructure complexity",
        }

        frustration_detected = (
            top_label in frustration_labels
            and top_score >= self._threshold
        )

        return FrustrationScore(
            label=top_label,
            score=top_score,
            frustration_detected=frustration_detected,
        )