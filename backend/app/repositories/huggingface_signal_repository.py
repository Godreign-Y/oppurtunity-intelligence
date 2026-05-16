"""
Repository for Hugging Face signals.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.huggingface_signal import HuggingFaceSignal


class HuggingFaceSignalRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict):

        query = select(HuggingFaceSignal).where(
            HuggingFaceSignal.model_id == data["model_id"]
        )

        result = await self.db.execute(query)
        existing = result.scalars().first()

        if existing:
            return

        self.db.add(HuggingFaceSignal(**data))
        await self.db.commit()
