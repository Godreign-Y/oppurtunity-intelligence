"""Semantic workflow pain scoring."""

from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer


PAIN_ANCHORS = [
    "manual repetitive workflow",
    "developer frustration",
    "tooling pain",
    "slow deployment process",
    "wasting engineering time",
    "bad developer experience",
    "workflow inefficiency",
    "debugging infrastructure issues",
    "operational bottleneck",
    "complex configuration problems",
    "time consuming engineering tasks",
    "frustrating API integration",
    "software workflow pain",
    "difficult DevOps process",
    "annoying debugging experience",
]

NEGATIVE_ANCHORS = [
    "fun tutorial",
    "project showcase",
    "happy announcement",
    "casual discussion",
    "general learning",
    "positive experience",
]


@dataclass
class WorkflowPainResult:
    relevance: float
    detected: bool
    positive_similarity: float
    negative_similarity: float


class WorkflowPainScorer:
    """Semantic workflow pain detector."""

    def __init__(
        self,
        model: SentenceTransformer,
    ) -> None:

        self._model = model

        self._pain_embeddings = self._model.encode(
            PAIN_ANCHORS,
            normalize_embeddings=True,
        )

        self._negative_embeddings = self._model.encode(
            NEGATIVE_ANCHORS,
            normalize_embeddings=True,
        )

    def score(self, text: str) -> WorkflowPainResult:

        embedding = self._model.encode(
            text,
            normalize_embeddings=True,
        )

        positive_scores = np.dot(
            self._pain_embeddings,
            embedding,
        )

        negative_scores = np.dot(
            self._negative_embeddings,
            embedding,
        )

        positive_similarity = float(np.max(positive_scores))

        negative_similarity = float(np.max(negative_scores))

        relevance = max(
            0.0,
            positive_similarity - (negative_similarity * 0.35),
        )

        relevance = min(1.0, relevance)

        detected = relevance >= 0.45

        return WorkflowPainResult(
            relevance=relevance,
            detected=detected,
            positive_similarity=positive_similarity,
            negative_similarity=negative_similarity,
        )