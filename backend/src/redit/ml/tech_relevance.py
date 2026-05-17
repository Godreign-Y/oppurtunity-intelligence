"""Semantic tech relevance via sentence-transformer cosine similarity."""

from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

TECH_ANCHORS: list[str] = [
    "Discussion about AI software APIs developer tools platforms and technology products",
    "Users reviewing LLM apps SaaS machine learning models plugins and integrations",
    "Complaints or feedback about a technology product feature reliability or workflow",
]

NON_TECH_ANCHORS: list[str] = [
    "Personal life story cooking travel pets sports unrelated to technology",
    "Random meme joke banter with no software or product discussion",
    "Political opinion entertainment gossip not about tech products",
]


@dataclass(frozen=True)
class TechRelevanceScore:
    """Semantic tech relevance scoring result."""

    tech_similarity: float
    non_tech_similarity: float
    margin: float
    is_relevant: bool


class TechRelevanceScorer:
    """
    CPU-friendly semantic gate using MiniLM embeddings.

    Compares post text against tech vs non-tech anchor phrases.
    """

    def __init__(
        self,
        model: SentenceTransformer,
        min_tech_similarity: float,
        min_margin: float,
    ) -> None:
        """Pre-encode anchor phrases once at startup."""
        self._model = model
        self._min_tech_similarity = min_tech_similarity
        self._min_margin = min_margin
        self._tech_emb = model.encode(
            TECH_ANCHORS,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        self._non_tech_emb = model.encode(
            NON_TECH_ANCHORS,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def score(self, text: str) -> TechRelevanceScore:
        """Compute tech relevance for a single post text."""
        embedding = self._model.encode(
            [text[:4000]],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        tech_sim = float(np.max(self._tech_emb @ embedding))
        non_tech_sim = float(np.max(self._non_tech_emb @ embedding))
        margin = tech_sim - non_tech_sim
        is_relevant = tech_sim >= self._min_tech_similarity and margin >= self._min_margin

        return TechRelevanceScore(
            tech_similarity=tech_sim,
            non_tech_similarity=non_tech_sim,
            margin=margin,
            is_relevant=is_relevant,
        )
