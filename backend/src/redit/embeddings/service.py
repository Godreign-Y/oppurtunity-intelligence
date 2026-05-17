"""Sentence-transformer embedding service."""

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Generate semantic embeddings for clustering."""

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def build_embedding_text(
        self,
        problem_statement: str,
        pain_category: str,
    ) -> str:
        """Construct embedding input."""

        return (
            f"{problem_statement} | {pain_category}"
        )

    def generate_embedding(
        self,
        problem_statement: str,
        pain_category: str,
    ) -> list[float]:
        """Generate 384-dim embedding."""

        text = self.build_embedding_text(
            problem_statement=problem_statement,
            pain_category=pain_category,
        )

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()