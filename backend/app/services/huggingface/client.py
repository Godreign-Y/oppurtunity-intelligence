"""
Hugging Face API client.
"""

import httpx


class HuggingFaceClient:
    """
    Handles communication with HF Hub API.
    """

    BASE_URL = "https://huggingface.co/api"

    async def fetch_models(self, limit: int = 20) -> list:
        """
        Fetch trending models.

        Args:
            limit (int): number of models

        Returns:
            list: models
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/models",
                params={
                    "limit": limit,
                    "sort": "downloads",
                    "direction": "-1",
                },
                timeout=30.0,
            )

        response.raise_for_status()
        return response.json()

    async def fetch_discussions(self, model_id: str) -> list:
        """
        Fetch discussions for a model.

        Args:
            model_id (str): model identifier

        Returns:
            list: discussion data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/models/{model_id}/discussions",
                timeout=30.0,
            )

        if response.status_code != 200:
            return []

        return response.json()