import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.database import Base

class Company(Base):
    """
    Database model representing a tracked company.
    """
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String)
    is_product_based: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    funding_events: Mapped[list["FundingEvent"]] = relationship(back_populates="company")

class FundingEvent(Base):
    """
    Database model representing a funding event for a company.
    """
    __tablename__ = "funding_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"))
    amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # in millions
    stage: Mapped[Optional[str]] = mapped_column(String)
    date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    source_url: Mapped[Optional[str]] = mapped_column(String)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    opportunity_score: Mapped[Optional[int]] = mapped_column(Integer)

    company: Mapped["Company"] = relationship(back_populates="funding_events")
