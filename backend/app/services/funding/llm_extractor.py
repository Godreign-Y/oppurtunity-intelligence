"""
app/services/funding/llm_extractor.py

Uses a hybrid approach: fast Regex extraction first,
falling back to Gemini or OpenRouter LLM if Regex fails.
"""

import json
import re
import httpx
import logging
from typing import Dict, Optional
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMExtractor:
    """
    Uses a hybrid approach: fast Regex extraction first,
    falling back to Gemini or OpenRouter LLM if Regex fails.
    """

    def __init__(self):
        self.gemini_key = settings.llm_api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"

    def regex_extract(self, text: str) -> Optional[Dict]:
        """
        Attempts to extract entities using fast Regex.
        Returns Dict if successful, None if it fails to find essential data.
        """
        amount = None
        amount_match = re.search(r'\$([0-9.]+)([mMbB])', text)
        if amount_match:
            try:
                val = float(amount_match.group(1))
                multiplier = amount_match.group(2).lower()
                if multiplier == 'b':
                    val *= 1000  # Convert billions to millions
                amount = val
            except ValueError:
                pass
            
        stage = None
        stage_match = re.search(r'(?i)(series\s+[a-h]|seed|pre-seed|angel)', text)
        if stage_match:
            stage = stage_match.group(1).title()
            
        company_name = None
        company_match = re.search(r'([A-Z][a-zA-Z0-9\s&\-]+?)\s+(raises|secures|announces|closes|lands)', text)
        if company_match:
            words = company_match.group(1).strip().split()
            company_name = " ".join(words[-3:]).strip()
            
        if company_name and amount:
            return {
                "company_name": company_name,
                "amount": amount,
                "stage": stage or "Seed",
                "investors": []
            }
        return None

    async def extract_entities(self, text: str) -> Optional[Dict]:
        """
        Extracts company_name, amount, stage, and investors from text.
        """
        # 1. Fast Regex attempt
        fast_result = self.regex_extract(text)
        if fast_result:
            logger.info(f"[LLMExtractor] Regex Succeeded: {fast_result['company_name']} (${fast_result['amount']}M)")
            return fast_result

        # 2. Fallback to LLM
        logger.info("[LLMExtractor] Regex extraction incomplete. Falling back to LLM...")
        prompt = f"""
        Extract funding data from the following news text.
        Return ONLY a JSON object with these keys:
        - company_name: string (Required)
        - amount: float (funding amount in millions, e.g., 25.5 for $25.5M. If not found, use null)
        - stage: string (e.g., 'Series A', 'Seed'. If not found, use null)
        - investors: list of strings (empty list if none found)

        Text:
        {text}
        """

        # If Gemini key is specified, hit Gemini directly
        if self.gemini_key:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(self.gemini_url, json=payload, timeout=15.0)
                    response.raise_for_status()
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        return None
                    output_text = candidates[0]["content"]["parts"][0]["text"]
                    return self._clean_and_parse_json(output_text)
                except Exception as e:
                    logger.error(f"[LLMExtractor] Gemini call failed: {e}")
                    # Let it fall back to OpenRouter below!

        # Fallback: Hit OpenRouter (already configured in main project)
        if settings.openrouter_api_key:
            try:
                client = AsyncOpenAI(
                    api_key=settings.openrouter_api_key,
                    base_url=settings.openrouter_base_url,
                )
                response = await client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[
                        {"role": "system", "content": "You are a precise JSON extractor. Respond only with raw JSON (no formatting fences)."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.0
                )
                output_text = response.choices[0].message.content or ""
                return self._clean_and_parse_json(output_text)
            except Exception as e:
                logger.error(f"[LLMExtractor] OpenRouter fallback failed: {e}")
                return None

        logger.warning("[LLMExtractor] No working LLM API credentials available.")
        return None

    def _clean_and_parse_json(self, raw_text: str) -> Optional[Dict]:
        """Strip markdown fences and load JSON."""
        try:
            clean = raw_text.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()
            return json.loads(clean)
        except Exception as e:
            logger.error(f"[LLMExtractor] JSON Parsing error: {e}")
            return None
