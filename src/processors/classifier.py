import httpx
import json
from src.config.settings import settings

class CompanyClassifier:
    """
    Determines if a company is product/SaaS or a service provider.
    """
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"

    async def classify_company(self, company_name: str, context: str) -> bool:
        """
        Returns True if the company is Product/SaaS/Technology focused.
        Returns False if it is a staffing, consulting, or outsourcing firm.
        """
        prompt = f"""
        Based on the following text about {company_name}, determine if the company is a product-based company (like SaaS, AI, Platform, Software tool) or a service-based company (like consulting, staffing, outsourcing agency).
        Return ONLY a JSON object with one key:
        - is_product_based: boolean (true or false)

        Text:
        {context}
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
                    return True # default to keeping it
                    
                output_text = candidates[0]["content"]["parts"][0]["text"]
                
                if "```json" in output_text:
                    output_text = output_text.split("```json")[1].split("```")[0].strip()
                elif "```" in output_text:
                    output_text = output_text.split("```")[1].split("```")[0].strip()
                    
                result = json.loads(output_text)
                return result.get("is_product_based", True)
            except Exception as e:
                print(f"LLM Classification failed: {e}")
                return True # Fail open to not lose data
