"""
app/services/market_pain/subreddit_registry.py

Curated registry of target subreddits for market pain intelligence.
Organized by domain to enable focused, low-noise data collection.
"""

# Enterprise technology & product discussion subreddits
TARGET_SUBREDDITS: list[str] = [
    "OpenAI",
    "ClaudeAI",
    "LocalLLaMA",
    "MachineLearning",
    "SaaS",
    "startups",
    "webdev",
    "programming",
    "devops",
    "dataengineering",
    "sysadmin",
    "salesforce",
    "aws",
    "kubernetes",
]

# Map subreddits to domain categories for weighting
SUBREDDIT_DOMAINS: dict[str, str] = {
    "OpenAI": "ai_ml",
    "ClaudeAI": "ai_ml",
    "LocalLLaMA": "ai_ml",
    "MachineLearning": "ai_ml",
    "SaaS": "enterprise_software",
    "startups": "enterprise_software",
    "webdev": "development",
    "programming": "development",
    "devops": "infrastructure",
    "dataengineering": "data_platform",
    "sysadmin": "infrastructure",
    "salesforce": "crm_enterprise",
    "aws": "cloud_platform",
    "kubernetes": "infrastructure",
}

# Domain weights — some domains are more enterprise-relevant
DOMAIN_WEIGHTS: dict[str, float] = {
    "ai_ml": 1.0,
    "enterprise_software": 0.95,
    "infrastructure": 0.90,
    "cloud_platform": 0.90,
    "data_platform": 0.85,
    "crm_enterprise": 0.85,
    "development": 0.75,
}


def get_domain_weight(subreddit: str) -> float:
    """Return the enterprise relevance weight for a subreddit."""
    domain = SUBREDDIT_DOMAINS.get(subreddit, "development")
    return DOMAIN_WEIGHTS.get(domain, 0.7)
