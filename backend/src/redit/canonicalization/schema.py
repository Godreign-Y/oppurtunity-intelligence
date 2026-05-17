"""Schema definitions for canonical problem intelligence."""

from pydantic import BaseModel, Field


class CanonicalProblem(BaseModel):
    """Structured canonicalized business problem extracted from a validated post."""

    problem_statement: str = Field(
        default="",
        description="Canonical, business-facing description of the pain point.",
    )

    pain_category: str = Field(
        default="",
        description="High-level business pain category.",
    )

    affected_tools: list[str] = Field(
        default_factory=list,
        description="Tools or platforms implicated in the pain.",
    )

    affected_platforms: list[str] = Field(
        default_factory=list,
        description="Affected infrastructure or cloud platform names.",
    )

    affected_persona: str = Field(
        default="",
        description="Primary personas affected by the problem.",
    )

    business_impact: str = Field(
        default="",
        description="Business consequence of the problem.",
    )

    urgency: str = Field(
        default="",
        description="Relative urgency or time-sensitivity of the problem.",
    )

    solution_category: str = Field(
        default="",
        description="Suggested solution opportunity category.",
    )

    possible_companies_affected: list[str] = Field(
        default_factory=list,
        description="Vendor/platform companies associated with the affected tooling ecosystem.",
    )

    raw_post_title: str = Field(
        default="",
        description="Original Reddit post title for traceability.",
    )

    raw_post_body: str = Field(
        default="",
        description="Original Reddit post body for traceability.",
    )