"""
Tracked query model.
"""

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base_class import Base


class TrackedQuery(Base):
    """
    Stores ingestion queries and their last execution timestamp.
    """

    __tablename__ = "tracked_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(50))
    last_run_at: Mapped[datetime] = mapped_column(DateTime)
