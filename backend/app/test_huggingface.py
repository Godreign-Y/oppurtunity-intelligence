"""
Temporary test script for Hugging Face ingestion.
"""

import asyncio

from app.core.database import AsyncSessionLocal
from app.services.huggingface.service import HuggingFaceIngestionService


async def test():
    async with AsyncSessionLocal() as db:
        service = HuggingFaceIngestionService(db)
        result = await service.ingest()
        print(len(result))


if __name__ == "__main__":
    asyncio.run(test())