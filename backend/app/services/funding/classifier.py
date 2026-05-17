"""
app/services/funding/classifier.py

Determines if a company is product/SaaS or a service provider.
"""

import json
import logging
from typing import Dict

from app.clients.llm import get_llm_client, get_llm_model

logger = logging.getLogger(__name__)


class CompanyClassifier:
    """
    Determines if a company is product/SaaS or a service provider.
    """

    def __init__(self):
        pass

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

        # Use NVIDIA NIM only.
        client = get_llm_client()
        if client:
            try:
                response = await client.chat.completions.create(
                    model=get_llm_model(),
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
                logger.error(f"[CompanyClassifier] NVIDIA NIM classification failed: {e}")
                return True  # Fail open to avoid dropping potentially valid companies

        logger.warning("[CompanyClassifier] NVIDIA_API_KEY is not configured. Failing open.")
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
