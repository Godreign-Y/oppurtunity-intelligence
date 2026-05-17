"""Known product → company mappings for dictionary extraction."""

from typing import Literal

KNOWN_PRODUCTS: dict[str, str] = {
    "ChatGPT": "OpenAI",
    "GPT-4": "OpenAI",
    "GPT-4o": "OpenAI",
    "OpenAI": "OpenAI",
    "Claude": "Anthropic",
    "Gemini": "Google",
    "Copilot": "Microsoft",
    "GitHub Copilot": "Microsoft",
    "Cursor": "Cursor",
    "Replit": "Replit",
    "Perplexity": "Perplexity",
    "Midjourney": "Midjourney",
    "Stable Diffusion": "Stability AI",
    "LangChain": "LangChain",
    "Llama": "Meta",
    "LocalLLaMA": "Meta",
    "Ollama": "Ollama",
    "Pinecone": "Pinecone",
    "Weaviate": "Weaviate",
    "Notion": "Notion",
    "Slack": "Slack",
    "Jira": "Atlassian",
    "Figma": "Figma",
    "Vercel": "Vercel",
    "Supabase": "Supabase",
    "Firebase": "Google",
    "AWS": "Amazon",
    "Azure": "Microsoft",
    "Snowflake": "Snowflake",
    "Databricks": "Databricks",
}

MatchSource = Literal["dictionary", "none"]


def extract_product_company(text: str) -> tuple[str | None, str | None, MatchSource]:
    """
    Longest-match-first dictionary lookup in combined post text.

    Returns:
        product name, company name, and match source.
    """
    haystack = text.lower()
    for product in sorted(KNOWN_PRODUCTS, key=len, reverse=True):
        if product.lower() in haystack:
            return product, KNOWN_PRODUCTS[product], "dictionary"
    return None, None, "none"


def is_known_company(company: str | None) -> bool:
    """Return True if company appears in the known products map."""
    if not company:
        return False
    return company in set(KNOWN_PRODUCTS.values())
