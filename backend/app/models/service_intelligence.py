"""Service-company intelligence models for Relanto capability matching."""

import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, BigInteger, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ServiceCompany(Base):
    __tablename__ = "service_companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False, unique=True, index=True)
    legal_name = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    headquarters = Column(String(255), nullable=True)
    founded_year = Column(Integer, nullable=True)
    employee_count = Column(Integer, nullable=True)
    revenue_range = Column(String(100), nullable=True)
    ai_maturity_level = Column(String(50), nullable=True)
    transformation_focus = Column(Text, nullable=True)
    market_positioning = Column(Text, nullable=True)
    primary_regions = Column(JSON, default=list)
    active_status = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    practices = relationship("ServicePractice", back_populates="company", cascade="all, delete-orphan")
    past_deals = relationship("ServicePastDeal", back_populates="company", cascade="all, delete-orphan")


class ServicePractice(Base):
    __tablename__ = "service_practices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("service_companies.id", ondelete="CASCADE"), nullable=False)
    practice_name = Column(String(255), nullable=False)
    practice_code = Column(String(50), nullable=False, unique=True)
    practice_category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    maturity_level = Column(String(50), nullable=True)
    strategic_priority = Column(String(50), nullable=True)
    delivery_strength = Column(Integer, nullable=True)
    bench_strength = Column(Integer, nullable=True)
    sme_count = Column(Integer, nullable=True)
    utilization_percentage = Column(Numeric(5, 2), nullable=True)
    growth_priority = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("ServiceCompany", back_populates="practices")
    opportunity_mappings = relationship("ServiceOpportunityPracticeMapping", back_populates="practice", cascade="all, delete-orphan")


class ServiceTechnology(Base):
    __tablename__ = "service_technologies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    technology_name = Column(String(255), nullable=False, unique=True)
    technology_category = Column(String(100), nullable=True)
    vendor = Column(String(100), nullable=True)
    maturity_level = Column(String(50), nullable=True)
    market_trend_score = Column(Integer, nullable=True)
    strategic_importance = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ServiceOpportunity(Base):
    __tablename__ = "service_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opportunity_name = Column(String(255), nullable=False)
    opportunity_code = Column(String(50), nullable=False, unique=True)
    opportunity_category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    market_growth_score = Column(Integer, nullable=True)
    implementation_complexity = Column(Integer, nullable=True)
    delivery_risk_level = Column(Integer, nullable=True)
    strategic_priority = Column(String(50), nullable=True)
    avg_deal_size_usd = Column(BigInteger, nullable=True)
    transformation_type = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    practice_mappings = relationship("ServiceOpportunityPracticeMapping", back_populates="opportunity", cascade="all, delete-orphan")


class ServiceOpportunityPracticeMapping(Base):
    __tablename__ = "service_opportunity_practice_mapping"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("service_opportunities.id", ondelete="CASCADE"), nullable=False)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("service_practices.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(Integer, nullable=False)
    mapping_type = Column(String(50), default="Primary")
    execution_dependency = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    opportunity = relationship("ServiceOpportunity", back_populates="practice_mappings")
    practice = relationship("ServicePractice", back_populates="opportunity_mappings")


class ServicePastDeal(Base):
    __tablename__ = "service_past_deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("service_companies.id", ondelete="CASCADE"), nullable=False)
    client_name = Column(String(255), nullable=True)
    project_name = Column(String(255), nullable=True)
    opportunity_type = Column(String(255), nullable=True)
    domain = Column(String(100), nullable=True)
    technologies_used = Column(JSON, default=list)
    deal_value_usd = Column(BigInteger, nullable=True)
    delivery_status = Column(String(100), nullable=True)
    profitability_score = Column(Integer, nullable=True)
    client_satisfaction_score = Column(Integer, nullable=True)
    transformation_outcome = Column(Text, nullable=True)
    strategic_value = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("ServiceCompany", back_populates="past_deals")


class RelantoOpportunityScore(Base):
    __tablename__ = "relanto_opportunity_scores"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_relanto_opportunity_score_source"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(100), nullable=False, index=True)
    source_id = Column(String(100), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    body = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    opportunity_category = Column(String(100), nullable=True, index=True)
    confidence = Column(Numeric(5, 4), nullable=True)
    score = Column(Integer, nullable=False, default=0)
    priority = Column(String(50), nullable=False, default="Medium")
    relanto_relevance_score = Column(Integer, nullable=False, default=0, index=True)
    practices = Column(JSON, default=list)
    past_deals = Column(JSON, default=list)
    reason = Column(Text, nullable=True)
    technologies = Column(JSON, default=list)
    pain_indicators = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
