"""
app/services/ai/inference.py

AI inference layer: takes normalized signals and produces explainable
opportunity intelligence using NVIDIA NIM.
"""

import json
import logging
from typing import Optional, Any

from app.clients.llm import get_llm_client, get_llm_model
from app.schemas.signal import UnifiedSignalSchema, AIOpportunityOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert IT opportunity intelligence analyst.
Given a set of structured signals extracted from a company's career pages, engineering blogs, and market pain signals (such as Reddit community workflow frustrations),
your task is to produce a concise, actionable opportunity assessment that incorporates capability mapping, temporal urgency, strategic fit, and organizational strengths.

IMPORTANT: If there is no data for a certain aspect, or if there is no data at all, clearly state that the data is missing. DO NOT hallucinate. If you do not have enough data to determine an opportunity, set detected_opportunity to 'Insufficient Data', confidence to 0.0, and explain in the reasoning.

Respond ONLY with a JSON object matching this schema (no markdown, no preamble):
{
  "detected_opportunity": "<short opportunity label or 'Insufficient Data'>",
  "confidence": <float 0.0–1.0>,
  "reasoning": ["<reason 1>", "<reason 2>", ...],
  "recommended_outreach": {
    "stakeholder": "<target stakeholder title>",
    "angle": "<one sentence outreach angle>"
  }
}"""


def _build_user_prompt(signals: list[UnifiedSignalSchema], company_name: str) -> str:
    """
    Build the user message for the LLM from a list of signals.

    Args:
        signals: Normalized signals to analyze.
        company_name: Company name.

    Returns:
        Formatted user prompt string.
    """
    pain_counter: dict[str, int] = {}
    tech_set: set[str] = set()
    opportunity_set: set[str] = set()
    evidence_samples: list[str] = []

    for signal in signals:
        for pain in signal.pain_indicators:
            pain_counter[pain] = pain_counter.get(pain, 0) + 1
        tech_set.update(signal.technologies)
        opportunity_set.update(signal.opportunity_mapping)
        evidence_samples.extend(signal.evidence[:2])

    sorted_pains = sorted(pain_counter.items(), key=lambda x: x[1], reverse=True)

    prompt = f"""Company: {company_name}
Total signals analyzed: {len(signals)}

Top Pain Indicators (by frequency):
{chr(10).join(f"  - {pain}: {count} occurrence(s)" for pain, count in sorted_pains[:6])}

Detected Technologies:
  {", ".join(sorted(tech_set)[:15]) or "None detected"}

Suggested Opportunity Types (from signal normalization):
  {", ".join(sorted(opportunity_set)[:6]) or "None"}

Evidence Samples:
{chr(10).join(f"  - {e}" for e in evidence_samples[:8])}

Based on the above, generate an opportunity intelligence assessment."""

    return prompt


def _build_market_pain_context(market_pain_signals: list) -> str:
    """
    Build a compressed market pain context section for the LLM prompt.

    Args:
        market_pain_signals: List of MarketPainSignalSchema objects.

    Returns:
        Formatted market pain context string.
    """
    if not market_pain_signals:
        return ""

    pain_categories: dict[str, int] = {}
    severities: list[str] = []
    practices: set[str] = set()
    sample_pains: list[str] = []

    def _get(s, key, default=None):
        return s.get(key, default) if isinstance(s, dict) else getattr(s, key, default)

    for sig in market_pain_signals[:10]:
        pain_cat = _get(sig, 'pain_category')
        if pain_cat:
            pain_categories[pain_cat] = pain_categories.get(pain_cat, 0) + 1
        severities.append(str(_get(sig, 'severity', 'unknown')))
        practices.update(_get(sig, 'matched_practices', []) or [])
        title = _get(sig, 'title')
        subreddit = _get(sig, 'subreddit', 'unknown')
        if title:
            sample_pains.append(f'  - [{subreddit}] {str(title)[:80]}')

    sorted_pains = sorted(pain_categories.items(), key=lambda x: x[1], reverse=True)

    section = f"""\n\nMarket Pain Intelligence (from Reddit community signals):
  Total pain signals detected: {len(market_pain_signals)}
  Top pain categories:
{chr(10).join(f'    - {cat}: {cnt} signal(s)' for cat, cnt in sorted_pains[:5])}
  Severity distribution: {', '.join(severities[:10])}
  Matched organizational practices: {', '.join(sorted(practices)[:6]) or 'None'}

  Sample community frustrations:
{chr(10).join(sample_pains[:5])}"""

    return section


async def run_ai_inference(
    signals: list[UnifiedSignalSchema],
    company_name: str,
    market_pain_signals: list | None = None,
) -> Optional[AIOpportunityOutput]:
    """
    Run LLM-based inference over a set of normalized signals.

    Args:
        signals: List of normalized UnifiedSignalSchema objects.
        company_name: Name of the company being analyzed.
        market_pain_signals: Optional list of MarketPainSignalSchema objects.

    Returns:
        AIOpportunityOutput with detected opportunity, confidence,
        reasoning, and recommended outreach. Returns None on failure.
    """
    if not signals and not market_pain_signals:
        logger.warning(f"[AIInference] No signals to analyze for {company_name}")
        return None

    client = get_llm_client()
    if not client:
        logger.warning("[AIInference] No LLM API key set; skipping AI inference.")
        return None

    user_prompt = _build_user_prompt(signals or [], company_name)

    # Append market pain context if available
    if market_pain_signals:
        user_prompt += _build_market_pain_context(market_pain_signals)

    try:
        response = await client.chat.completions.create(
            model=get_llm_model(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=600,
            temperature=0.2,
        )

        raw = response.choices[0].message.content or ""
        # Strip any accidental markdown fences
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(clean)

        return AIOpportunityOutput(
            detected_opportunity=data.get("detected_opportunity", "Unknown"),
            confidence=float(data.get("confidence", 0.5)),
            reasoning=data.get("reasoning", []),
            recommended_outreach=data.get("recommended_outreach", {}),
        )

    except json.JSONDecodeError as exc:
        logger.error(f"[AIInference] JSON parse error: {exc}")
        return None
    except Exception as exc:
        logger.error(f"[AIInference] LLM call failed: {exc}")
        return None
