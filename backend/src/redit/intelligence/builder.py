"""Build validated intelligence JSON from pipeline context."""

from uuid import UUID

from redit.models.intelligence import IntelligenceRecord, SCHEMA_VERSION
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class IntelligenceBuilder:
    """Assemble Step-10 intelligence document from accumulated stage metadata."""

    def build(
        self,
        post: RawRedditPost,
        context: PipelineContext,
        run_id: UUID,
    ) -> IntelligenceRecord:
        """Map post + pipeline context to IntelligenceRecord."""
        meta = context.accumulated

        tech_confidence = float(meta.get("tech_confidence", 0.0))
        frustration_score = float(meta.get("frustration_score", 0.0))

        return IntelligenceRecord(
            schema_version=SCHEMA_VERSION,
            post_id=post.id,
            subreddit=post.subreddit,
            title=post.title,
            body=post.body,
            upvotes=post.score,
            timestamp=post.created_at,
            permalink=post.permalink,
            product=meta.get("product"),
            company=meta.get("company"),
            tech_confidence=round(tech_confidence, 4),
            frustration_score=round(frustration_score, 4),
            frustration_detected=bool(meta.get("frustration_detected", False)),
            business_relevance=round(float(meta.get("business_relevance", 0.0)), 4),
            workflow_pain_detected=bool(meta.get("workflow_pain_detected", False)),
            problem_statement=meta.get("problem_statement", ""),
            pain_category=meta.get("pain_category", ""),
            affected_tools=list(meta.get("affected_tools", [])),
            affected_platforms=list(meta.get("affected_platforms", [])),
            affected_persona=meta.get("affected_persona", ""),
            business_impact=meta.get("business_impact", ""),
            urgency=meta.get("urgency", ""),
            solution_category=meta.get("solution_category", ""),
            ingestion_run_id=str(run_id),
            matched_keywords=list(meta.get("workflow_matched_keywords", [])),
        )
