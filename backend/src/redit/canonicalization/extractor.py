"""Hybrid semantic canonicalization using Groq LLM."""

import json
import os
import re
from typing import Any

from groq import Groq

from redit.canonicalization.prompts import (
    CANONICALIZATION_FEW_SHOTS,
    CANONICALIZATION_INSTRUCTION,
)
from redit.canonicalization.schema import CanonicalProblem
from redit.models.reddit import RawRedditPost

MODEL_NAME = "llama-3.3-70b-versatile"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _build_prompt(post: RawRedditPost) -> str:
    few_shot_text = ""

    for example in CANONICALIZATION_FEW_SHOTS:
        few_shot_text += (
            f"\nINPUT:\n{example['input']}\n"
            f"OUTPUT:\n{json.dumps(example['output'], indent=2)}\n"
        )

    return f"""
{CANONICALIZATION_INSTRUCTION}

IMPORTANT:
Infer the MAJOR vendor/platform companies associated with the
affected tools or infrastructure ecosystem.

Examples:
- AWS -> Amazon
- Kubernetes/GKE -> Google
- Azure/GitHub -> Microsoft
- Terraform -> HashiCorp
- Docker -> Docker Inc

Return them in:
possible_companies_affected

FEW SHOT EXAMPLES:
{few_shot_text}

POST TITLE:
{post.title}

POST BODY:
{post.body}

Return STRICT JSON ONLY.
"""


def _fallback_problem(post: RawRedditPost) -> CanonicalProblem:
    return CanonicalProblem(
        problem_statement=_clean_text(post.title)
        or "Operational workflow pain",
        pain_category="Workflow Pain",
        affected_tools=[],
        affected_platforms=[],
        affected_persona="Technical teams",
        business_impact="workflow disruption",
        urgency="medium",
        solution_category="Workflow optimization",
        possible_companies_affected=[],
        raw_post_title=post.title,
        raw_post_body=post.body,
    )


def canonicalize_post(
    post: RawRedditPost,
    metadata: dict[str, Any] | None = None,
) -> CanonicalProblem:
    """Canonicalize Reddit complaint into structured business pain."""

    _ = metadata

    try:
        prompt = _build_prompt(post)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": CANONICALIZATION_INSTRUCTION,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content or "{}"

        if isinstance(content, str):
            parsed = json.loads(content)
        else:
            parsed = content

        parsed["raw_post_title"] = post.title
        parsed["raw_post_body"] = post.body

        parsed.setdefault("possible_companies_affected", [])

        canonical = CanonicalProblem.model_validate(parsed)

        canonical.problem_statement = _clean_text(
            canonical.problem_statement
        )

        canonical.pain_category = _clean_text(
            canonical.pain_category
        )

        canonical.business_impact = _clean_text(
            canonical.business_impact
        )

        canonical.solution_category = _clean_text(
            canonical.solution_category
        )

        canonical.possible_companies_affected = [
            _clean_text(company)
            for company in canonical.possible_companies_affected
            if company
        ]

        return canonical

    except Exception:
        return _fallback_problem(post)