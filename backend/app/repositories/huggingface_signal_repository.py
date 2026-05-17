"""
Repository for Hugging Face signals.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.huggingface_signal import HuggingFaceSignal


class HuggingFaceSignalRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict):

        query = select(HuggingFaceSignal).where(
            HuggingFaceSignal.model_id == data["model_id"]
        )

        result = self.db.execute(query)
        existing = result.scalars().first()

        if existing:
            return

        self.db.add(HuggingFaceSignal(**data))
        self.db.commit()
