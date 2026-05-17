import httpx
import json
import re
from typing import Dict, Optional
from src.config.settings import settings

class LLMExtractor:
    """
    Uses a hybrid approach: fast Regex extraction first, 
    falling back to Gemini LLM if Regex fails.
    """
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"

    def regex_extract(self, text: str) -> Optional[Dict]:
        """
        Attempts to extract entities using fast Regex.
        Returns Dict if successful, None if it fails to find essential data.
        """
        amount = None
        # Look for $X.XM or $X.XB
        amount_match = re.search(r'\$([0-9.]+)([mMbB])', text)
        if amount_match:
            try:
                val = float(amount_match.group(1))
                multiplier = amount_match.group(2).lower()
                if multiplier == 'b':
                    val *= 1000 # Convert billions to millions
                amount = val
            except ValueError:
                pass
            
        stage = None
        # Look for common funding stages
        stage_match = re.search(r'(?i)(series\s+[a-h]|seed|pre-seed|angel)', text)
        if stage_match:
            stage = stage_match.group(1).title()
            
        company_name = None
        # Look for Capitalized words before "raises", "secures", "announces"
        company_match = re.search(r'([A-Z][a-zA-Z0-9\s&\-]+?)\s+(raises|secures|announces|closes|lands)', text)
        if company_match:
            words = company_match.group(1).strip().split()
            # Grab up to the last 3 words to avoid giant strings
            company_name = " ".join(words[-3:]).strip()
            
        # We only consider regex "successful" if we at least found a company and an amount
        if company_name and amount:
            return {
                "company_name": company_name,
                "amount": amount,
                "stage": stage,
                "investors": [] # Regex for investors is too fragile, leave empty
            }
        return None

    async def extract_entities(self, text: str) -> Optional[Dict]:
        """
        Extracts company_name, amount, stage, and investors from text.
        """
        # 1. Fast Regex attempt
        fast_result = self.regex_extract(text)
        if fast_result:
            print(f"  -> Regex Extraction Succeeded: {fast_result['company_name']} (${fast_result['amount']}M)")
            return fast_result

        # 2. Fallback to LLM if Regex fails
        print("  -> Regex extraction incomplete. Falling back to LLM...")
        prompt = f"""
        Extract funding data from the following news text.
        Return ONLY a JSON object with these keys:
        - company_name: string
        - amount: float (funding amount in millions, e.g., 25.5 for $25.5M. If not found, use null)
        - stage: string (e.g., 'Series A', 'Seed'. If not found, use null)
        - investors: list of strings (empty list if none found)

        Text:
        {text}
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.url, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                candidates = data.get("candidates", [])
                if not candidates:
                    return None
                    
                output_text = candidates[0]["content"]["parts"][0]["text"]
                
                # Clean markdown JSON wrapping if present
                if "```json" in output_text:
                    output_text = output_text.split("```json")[1].split("```")[0].strip()
                elif "```" in output_text:
                    output_text = output_text.split("```")[1].split("```")[0].strip()
                    
                return json.loads(output_text)
            except Exception as e:
                print(f"LLM Extraction failed: {e}")
                return None
