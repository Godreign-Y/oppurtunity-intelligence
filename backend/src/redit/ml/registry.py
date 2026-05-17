"""Load and hold CPU-friendly models for the app lifetime."""

from sentence_transformers import SentenceTransformer

from redit.config.settings import Settings
from redit.ml.frustration import FrustrationAnalyzer
from redit.ml.tech_relevance import TechRelevanceScorer
from redit.ml.workflow_pain import WorkflowPainScorer
from redit.utils.logging import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    """
    Singleton-style registry for models loaded once at startup.

    Future:
    - clustering embeddings
    - summarization models
    - rerankers
    - local LLMs
    """

    def __init__(self, settings: Settings) -> None:
        """Store settings; models are None until load()."""

        self._settings = settings

        self._tech_scorer: TechRelevanceScorer | None = None
        self._frustration: FrustrationAnalyzer | None = None

        self.workflow_pain: WorkflowPainScorer | None = None

        self._loaded = False

    @property
    def tech_scorer(self) -> TechRelevanceScorer:
        """Return tech relevance scorer."""

        if self._tech_scorer is None:
            raise RuntimeError(
                "ModelRegistry not loaded. Call load() during app startup."
            )

        return self._tech_scorer

    @property
    def frustration(self) -> FrustrationAnalyzer:
        """Return semantic frustration analyzer."""

        if self._frustration is None:
            raise RuntimeError(
                "ModelRegistry not loaded. Call load() during app startup."
            )

        return self._frustration

    @property
    def is_loaded(self) -> bool:
        """Whether models have been loaded."""

        return self._loaded

    def load(self) -> None:
        """Load ML models once during app startup."""

        if self._loaded:
            return

        logger.info(
            "Loading ML models",
            extra={
                "sentence_transformer_model":
                    self._settings.sentence_transformer_model
            },
        )

        # =========================================================
        # Shared Sentence Transformer
        # =========================================================

        transformer = SentenceTransformer(
            self._settings.sentence_transformer_model
        )

        # =========================================================
        # Workflow Pain Scorer
        # =========================================================

        self.workflow_pain = WorkflowPainScorer(
            model=transformer,
        )

        # =========================================================
        # Tech Relevance Scorer
        # =========================================================

        self._tech_scorer = TechRelevanceScorer(
            model=transformer,
            min_tech_similarity=self._settings.tech_similarity_min,
            min_margin=self._settings.tech_similarity_margin_min,
        )

        # =========================================================
        # Semantic Frustration Analyzer
        # =========================================================

        self._frustration = FrustrationAnalyzer(
            frustration_threshold=0.55,
        )

        self._loaded = True

        logger.info("ML models loaded successfully")

    def unload(self) -> None:
        """Release references (best-effort cleanup)."""

        self._tech_scorer = None
        self._frustration = None
        self.workflow_pain = None

        self._loaded = False