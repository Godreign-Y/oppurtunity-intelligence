"""
Raw signal model.
"""

from sqlalchemy import String, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import UniqueConstraint
from app.db.base_class import Base


class RawSignal(Base):
    """
    Stores raw ingested signals.
    """

    __tablename__ = "raw_signals"

    __table_args__ = (
        UniqueConstraint(
            "source",
            "external_id",
            name="uq_source_external_id"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    external_id: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    metadata_json: Mapped[dict] = mapped_column(JSON)
