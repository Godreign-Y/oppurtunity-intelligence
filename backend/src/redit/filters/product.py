"""Steps 6–7 — product extraction and business validation."""

import asyncio

from redit.config.settings import Settings
from redit.data.known_products import extract_product_company, is_known_company
from redit.filters.base import FilterStage
from redit.models.pipeline import FilterDecision, FilterResult, PipelineStageName
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class ProductExtractionFilter(FilterStage):
    """Extract product/company via dictionary (enrichment-only, never rejects)."""

    @property
    def stage_name(self) -> PipelineStageName:
        """Stage identifier."""
        return PipelineStageName.PRODUCT_EXTRACTION

    async def apply(self, post: RawRedditPost, context: PipelineContext) -> FilterResult:
        """Attach product/company metadata when found."""
        product, company, source = await asyncio.to_thread(
            extract_product_company,
            post.combined_text,
        )
        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
            metadata={
                "product": product,
                "company": company,
                "product_match_source": source,
            },
        )


class BusinessValidationFilter(FilterStage):
    """Require commercial signal: known product/company or workflow pain."""

    def __init__(self, settings: Settings) -> None:
        """Load minimum business relevance threshold."""
        self._min_relevance = settings.min_business_relevance

    @property
    def stage_name(self) -> PipelineStageName:
        """Stage identifier."""
        return PipelineStageName.BUSINESS_VALIDATION

    async def apply(self, post: RawRedditPost, context: PipelineContext) -> FilterResult:
        """Reject posts with no product and insufficient business/workflow signal."""
        _ = post
        meta = context.accumulated
        product = meta.get("product")
        company = meta.get("company")
        workflow_pain = bool(meta.get("workflow_pain_detected", False))
        business_relevance = float(meta.get("business_relevance", 0.0))

        has_known_business = bool(product) or is_known_company(company)
        if has_known_business or workflow_pain:
            return FilterResult(
                stage=self.stage_name,
                decision=FilterDecision.PASS,
                metadata={"business_validated": True},
            )

        if business_relevance >= self._min_relevance:
            return FilterResult(
                stage=self.stage_name,
                decision=FilterDecision.PASS,
                metadata={"business_validated": True, "via": "relevance_score"},
            )

        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.REJECT,
            reason_code="UNKNOWN_BUSINESS",
            detail="no known product/company and no workflow pain signal",
        )
