"""Find likely decision makers per company opportunity."""

from urllib.parse import quote_plus

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.company import Company
from app.services.service_intelligence.service import list_relanto_opportunities


PRACTICE_PERSONAS = {
    "PRA_DATA_AI": ["Chief Data Officer", "VP Data", "Head of AI", "Director Data Engineering"],
    "PRA_AI_LAB": ["Head of AI", "VP Product AI", "Director Innovation", "AI Platform Lead"],
    "PRA_DIGITAL": ["VP Engineering", "Head of Platform", "Director DevOps", "CTO"],
    "PRA_SALESFORCE": ["VP Revenue Operations", "Salesforce Director", "CRM Transformation Lead"],
    "PRA_PLANNING": ["VP Finance", "Head of Planning", "FP&A Director", "Operations Strategy Lead"],
}


def derive_domain(company: Company | None, company_name: str) -> str | None:
    if company and company.domain:
        return company.domain.replace("https://", "").replace("http://", "").strip("/")
    return None


def personas_for_practices(practices: list[dict]) -> list[str]:
    personas: list[str] = []
    for practice in practices:
        personas.extend(PRACTICE_PERSONAS.get(practice.get("practice_code"), []))
    if not personas:
        personas = ["CTO", "VP Engineering", "Head of Platform"]
    return list(dict.fromkeys(personas))[:5]


async def find_decision_makers(domain: str | None, company_name: str, personas: list[str]) -> list[dict]:
    """Use Hunter when available, otherwise return persona + LinkedIn search leads."""
    leads: list[dict] = []
    if settings.hunter_api_key and domain:
        params = {
            "domain": domain,
            "api_key": settings.hunter_api_key,
            "limit": 10,
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://api.hunter.io/v2/domain-search", params=params)
                response.raise_for_status()
                emails = response.json().get("data", {}).get("emails", [])
            persona_words = tuple(word.lower() for persona in personas for word in persona.split())
            for item in emails:
                position = item.get("position") or ""
                if persona_words and not any(word in position.lower() for word in persona_words):
                    continue
                leads.append({
                    "first_name": item.get("first_name"),
                    "last_name": item.get("last_name"),
                    "title": position,
                    "email": item.get("value"),
                    "linkedin_url": item.get("linkedin"),
                    "confidence": item.get("confidence"),
                    "source": "hunter",
                })
        except Exception:
            leads = []

    if leads:
        return leads[:5]

    return [
        {
            "first_name": None,
            "last_name": None,
            "title": persona,
            "email": None,
            "linkedin_url": f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(company_name + ' ' + persona)}",
            "confidence": None,
            "source": "linkedin_search",
        }
        for persona in personas[:4]
    ]


async def list_outreach_recommendations(db: Session, company_name: str | None = None) -> list[dict]:
    opportunities = list_relanto_opportunities(db, company_name=company_name)
    recommendations: list[dict] = []
    contact_cache: dict[tuple[str | None, tuple[str, ...]], list[dict]] = {}
    for opportunity in opportunities[:12]:
        company = db.query(Company).filter(Company.name == opportunity["company_name"]).first()
        domain = derive_domain(company, opportunity["company_name"])
        personas = personas_for_practices(opportunity.get("practices") or [])
        cache_key = (domain, tuple(personas))
        if cache_key not in contact_cache:
            contact_cache[cache_key] = await find_decision_makers(domain, opportunity["company_name"], personas)
        decision_makers = contact_cache[cache_key]
        recommendations.append({
            "opportunity_id": opportunity["id"],
            "company_name": opportunity["company_name"],
            "opportunity": opportunity["opportunity_category"],
            "source": opportunity["source"],
            "score": opportunity["score"],
            "relanto_relevance_score": opportunity["relanto_relevance_score"],
            "priority": opportunity["priority"],
            "practices": opportunity.get("practices") or [],
            "suggested_personas": personas,
            "decision_makers": decision_makers,
            "source_url": opportunity.get("source_url"),
            "angle": f"Lead with Relanto's {', '.join(p['practice_name'] for p in opportunity.get('practices', [])[:2]) or 'delivery'} capability for {opportunity['opportunity_category']}.",
        })
    return recommendations
