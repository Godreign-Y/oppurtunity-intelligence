"""
app/services/market_pain/entity_extractor.py

Phase 3 — Product, company, technology, and workflow entity extraction.
Uses a curated dictionary + regex patterns. No spaCy dependency needed
for MVP — rule-based extraction with high precision.
"""

import re
import logging

from app.services.market_pain.schemas import FilteredPost, ExtractedEntities

logger = logging.getLogger(__name__)

# Known product → company mapping registry
KNOWN_PRODUCTS: dict[str, str] = {
    # AI/ML
    "chatgpt": "OpenAI",
    "gpt-4": "OpenAI",
    "gpt-4o": "OpenAI",
    "gpt-3.5": "OpenAI",
    "openai": "OpenAI",
    "dall-e": "OpenAI",
    "whisper": "OpenAI",
    "claude": "Anthropic",
    "anthropic": "Anthropic",
    "gemini": "Google",
    "bard": "Google",
    "vertex ai": "Google",
    "copilot": "Microsoft",
    "github copilot": "Microsoft",
    "cursor": "Cursor",
    "devin": "Cognition",
    "v0": "Vercel",
    "perplexity": "Perplexity",
    "midjourney": "Midjourney",
    "stable diffusion": "Stability AI",
    "hugging face": "Hugging Face",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "ollama": "Ollama",
    "groq": "Groq",
    "mistral": "Mistral AI",
    "cohere": "Cohere",
    "together ai": "Together AI",

    # Cloud & Infrastructure
    "aws": "Amazon",
    "s3": "Amazon",
    "lambda": "Amazon",
    "ec2": "Amazon",
    "eks": "Amazon",
    "sagemaker": "Amazon",
    "gcp": "Google",
    "bigquery": "Google",
    "azure": "Microsoft",
    "azure devops": "Microsoft",
    "vercel": "Vercel",
    "netlify": "Netlify",
    "cloudflare": "Cloudflare",
    "digitalocean": "DigitalOcean",
    "heroku": "Salesforce",
    "railway": "Railway",
    "fly.io": "Fly.io",
    "supabase": "Supabase",
    "firebase": "Google",
    "neon": "Neon",
    "planetscale": "PlanetScale",

    # Enterprise Software
    "salesforce": "Salesforce",
    "servicenow": "ServiceNow",
    "jira": "Atlassian",
    "confluence": "Atlassian",
    "atlassian": "Atlassian",
    "slack": "Salesforce",
    "notion": "Notion",
    "linear": "Linear",
    "asana": "Asana",
    "monday.com": "Monday.com",
    "hubspot": "HubSpot",
    "zendesk": "Zendesk",
    "intercom": "Intercom",
    "stripe": "Stripe",
    "twilio": "Twilio",
    "segment": "Twilio",
    "snowflake": "Snowflake",
    "databricks": "Databricks",
    "datadog": "Datadog",
    "splunk": "Cisco",
    "pagerduty": "PagerDuty",
    "terraform": "HashiCorp",
    "vault": "HashiCorp",
    "docker": "Docker",
    "kubernetes": "CNCF",
    "grafana": "Grafana Labs",
    "elastic": "Elastic",
    "elasticsearch": "Elastic",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "kafka": "Confluent",
    "airflow": "Apache",
    "dbt": "dbt Labs",
    "postman": "Postman",
    "figma": "Figma",
}

# Technology keywords for extraction
TECH_PATTERNS: list[str] = [
    "kubernetes", "k8s", "docker", "terraform", "ansible", "pulumi",
    "aws", "gcp", "azure", "lambda", "s3", "ec2", "eks", "ecs",
    "react", "next.js", "vue", "angular", "svelte", "typescript",
    "python", "go", "rust", "java", "node.js", "ruby",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "kafka", "rabbitmq", "grpc", "graphql", "rest api",
    "ci/cd", "github actions", "gitlab ci", "jenkins", "argocd",
    "prometheus", "grafana", "datadog", "opentelemetry",
    "llm", "rag", "vector database", "embeddings", "fine-tuning",
    "langchain", "llamaindex", "pinecone", "weaviate", "chromadb",
    "microservices", "monolith", "serverless", "edge computing",
]

# Workflow patterns
WORKFLOW_PATTERNS: list[str] = [
    "deployment pipeline", "ci/cd pipeline", "data pipeline",
    "etl", "elt", "data ingestion", "data warehouse",
    "authentication flow", "oauth flow", "sso",
    "monitoring", "alerting", "incident response",
    "code review", "pull request", "merge conflict",
    "testing pipeline", "qa process", "staging environment",
    "release process", "feature flag", "canary deployment",
    "backup", "disaster recovery", "failover",
    "onboarding", "provisioning", "access management",
]


def extract_entities(post: FilteredPost) -> ExtractedEntities:
    """
    Extract products, companies, technologies, and workflows from a post.

    Uses dictionary lookup + regex pattern matching.
    Case-insensitive matching against the KNOWN_PRODUCTS registry.

    Args:
        post: A relevance-filtered post.

    Returns:
        ExtractedEntities with all detected entities.
    """
    combined = f"{post.title} {post.body}".lower()

    # Extract products and companies
    products: list[str] = []
    companies: list[str] = []
    for product_key, company in KNOWN_PRODUCTS.items():
        if product_key in combined:
            product_display = product_key.title()
            if product_display not in products:
                products.append(product_display)
            if company not in companies:
                companies.append(company)

    # Extract technologies
    technologies: list[str] = []
    for tech in TECH_PATTERNS:
        if tech in combined and tech not in technologies:
            technologies.append(tech)

    # Extract workflow mentions
    workflows: list[str] = []
    for wf in WORKFLOW_PATTERNS:
        if wf in combined and wf not in workflows:
            workflows.append(wf)

    return ExtractedEntities(
        products=products,
        companies=companies,
        technologies=technologies,
        workflows=workflows,
    )


def batch_extract_entities(
    posts: list[FilteredPost],
) -> list[tuple[FilteredPost, ExtractedEntities]]:
    """
    Run entity extraction on a batch of filtered posts.

    Args:
        posts: List of FilteredPost objects.

    Returns:
        List of (post, entities) tuples.
    """
    results = []
    for post in posts:
        entities = extract_entities(post)
        results.append((post, entities))

    total_products = sum(len(e.products) for _, e in results)
    logger.info(
        f"[EntityExtractor] Extracted entities from {len(posts)} posts: "
        f"{total_products} product mentions found"
    )
    return results
