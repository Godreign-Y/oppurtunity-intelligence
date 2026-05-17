"""
app/services/funding/classifier.py

Determines if a company is product/SaaS or a service provider.
"""

import json
import httpx
import logging
from typing import Dict
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class CompanyClassifier:
    """
    Determines if a company is product/SaaS or a service provider.
    """

    def __init__(self):
        self.gemini_key = settings.llm_api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"

    async def classify_company(self, company_name: str, context: str) -> bool:
        """
        Returns True if the company is Product/SaaS/Technology focused.
        Returns False if it is a staffing, consulting, or outsourcing firm.
        """
        prompt = f"""
        Based on the following text about {company_name}, determine if the company is a product-based company (like SaaS, AI, Platform, Software tool, consumer tech) or a service-based company (like IT services, staffing agency, consulting group, outsourcing shop).
        Return ONLY a JSON object with one key:
        - is_product_based: boolean (true or false)

        Text:
        {context}
        """

        # Try Gemini direct first
        if self.gemini_key:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(self.gemini_url, json=payload, timeout=10.0)
                    response.raise_for_status()
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        output_text = candidates[0]["content"]["parts"][0]["text"]
                        return self._parse_result(output_text)
                except Exception as e:
                    logger.error(f"[CompanyClassifier] Gemini classification failed: {e}")
                    # Allow fallback

        # Fallback to OpenRouter
        if settings.openrouter_api_key:
            try:
                client = AsyncOpenAI(
                    api_key=settings.openrouter_api_key,
                    base_url=settings.openrouter_base_url,
                )
                response = await client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[
                        {"role": "system", "content": "You are a precise classifier. Respond only with raw JSON (no formatting fences)."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.0
                )
                output_text = response.choices[0].message.content or ""
                return self._parse_result(output_text)
            except Exception as e:
                logger.error(f"[CompanyClassifier] OpenRouter classification failed: {e}")
                return True  # Fail open to avoid dropping potentially valid companies

        logger.warning("[CompanyClassifier] No LLM API credentials available. Failing open.")
        return True

    def _parse_result(self, raw_text: str) -> bool:
        try:
            clean = raw_text.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()
            result = json.loads(clean)
            return result.get("is_product_based", True)
        except Exception as e:
            logger.error(f"[CompanyClassifier] Error parsing classification: {e}")
            return True
