"""
Hugging Face signal model.
"""

from sqlalchemy import String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base_class import Base


class HuggingFaceSignal(Base):
    __tablename__ = "huggingface_signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[str] = mapped_column(String(255), unique=True)
    source_url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    metadata_json: Mapped[dict] = mapped_column(JSON)
