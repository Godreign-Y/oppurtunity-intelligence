"""
Hugging Face ingestion service.
"""

from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.huggingface.client import HuggingFaceClient
from app.services.huggingface.parser import parse_models
from app.repositories.huggingface_signal_repository import HuggingFaceSignalRepository

class HuggingFaceIngestionService:
    """
    Stable Hugging Face ingestion service (no discussions).
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = HuggingFaceClient()
        self.repo = HuggingFaceSignalRepository(db)

    async def ingest(self) -> List[dict]:
        """
        Fetch trending models and store them.
        """

        raw_models = await self.client.fetch_models()
        parsed_models = parse_models(raw_models)

        for model in parsed_models:
            await self.repo.create(
                {
                    "model_id": model["model_id"],
                    "source_url": model["source_url"],
                    "created_at": datetime.utcnow(),
                    "metadata_json": {
                        "downloads": model["downloads"],
                        "likes": model["likes"],
                        "tags": model["tags"],
                        "pipeline_tag": model["pipeline_tag"],
                    },
                }
        )
            

        return parsed_models
