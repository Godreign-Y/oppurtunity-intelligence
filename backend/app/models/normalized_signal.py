"""
Normalized signal model.
"""

from sqlalchemy import String, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base_class import Base


class NormalizedSignal(Base):
    """
    Stores normalized GitHub signals.
    """

    __tablename__ = "normalized_signals"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ✅ IMPORTANT CHANGE: link to github_signals
    github_signal_id: Mapped[int] = mapped_column(ForeignKey("github_signals.id"))

    signal_type: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(50))
    ecosystem: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
