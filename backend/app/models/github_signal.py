"""
GitHub signal model.
"""

from sqlalchemy import String, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base_class import Base


class GitHubSignal(Base):
    __tablename__ = "github_signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    metadata_json: Mapped[dict] = mapped_column(JSON)
    opportunity_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
