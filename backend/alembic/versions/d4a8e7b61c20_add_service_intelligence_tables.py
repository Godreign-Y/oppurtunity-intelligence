"""add service intelligence tables

Revision ID: d4a8e7b61c20
Revises: c3b7d9a2f4e1
Create Date: 2026-05-17 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d4a8e7b61c20"
down_revision: Union[str, None] = "c3b7d9a2f4e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "service_companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("linkedin_url", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("headquarters", sa.String(length=255), nullable=True),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("revenue_range", sa.String(length=100), nullable=True),
        sa.Column("ai_maturity_level", sa.String(length=50), nullable=True),
        sa.Column("transformation_focus", sa.Text(), nullable=True),
        sa.Column("market_positioning", sa.Text(), nullable=True),
        sa.Column("primary_regions", sa.JSON(), nullable=True),
        sa.Column("active_status", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_name"),
    )
    op.create_index(op.f("ix_service_companies_company_name"), "service_companies", ["company_name"], unique=False)

    op.create_table(
        "service_technologies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("technology_name", sa.String(length=255), nullable=False),
        sa.Column("technology_category", sa.String(length=100), nullable=True),
        sa.Column("vendor", sa.String(length=100), nullable=True),
        sa.Column("maturity_level", sa.String(length=50), nullable=True),
        sa.Column("market_trend_score", sa.Integer(), nullable=True),
        sa.Column("strategic_importance", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("technology_name"),
    )

    op.create_table(
        "service_opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("opportunity_name", sa.String(length=255), nullable=False),
        sa.Column("opportunity_code", sa.String(length=50), nullable=False),
        sa.Column("opportunity_category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("market_growth_score", sa.Integer(), nullable=True),
        sa.Column("implementation_complexity", sa.Integer(), nullable=True),
        sa.Column("delivery_risk_level", sa.Integer(), nullable=True),
        sa.Column("strategic_priority", sa.String(length=50), nullable=True),
        sa.Column("avg_deal_size_usd", sa.BigInteger(), nullable=True),
        sa.Column("transformation_type", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("opportunity_code"),
    )

    op.create_table(
        "service_practices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("practice_name", sa.String(length=255), nullable=False),
        sa.Column("practice_code", sa.String(length=50), nullable=False),
        sa.Column("practice_category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("maturity_level", sa.String(length=50), nullable=True),
        sa.Column("strategic_priority", sa.String(length=50), nullable=True),
        sa.Column("delivery_strength", sa.Integer(), nullable=True),
        sa.Column("bench_strength", sa.Integer(), nullable=True),
        sa.Column("sme_count", sa.Integer(), nullable=True),
        sa.Column("utilization_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("growth_priority", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["service_companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("practice_code"),
    )

    op.create_table(
        "service_past_deals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_name", sa.String(length=255), nullable=True),
        sa.Column("project_name", sa.String(length=255), nullable=True),
        sa.Column("opportunity_type", sa.String(length=255), nullable=True),
        sa.Column("domain", sa.String(length=100), nullable=True),
        sa.Column("technologies_used", sa.JSON(), nullable=True),
        sa.Column("deal_value_usd", sa.BigInteger(), nullable=True),
        sa.Column("delivery_status", sa.String(length=100), nullable=True),
        sa.Column("profitability_score", sa.Integer(), nullable=True),
        sa.Column("client_satisfaction_score", sa.Integer(), nullable=True),
        sa.Column("transformation_outcome", sa.Text(), nullable=True),
        sa.Column("strategic_value", sa.String(length=100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["service_companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "service_opportunity_practice_mapping",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("practice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relevance_score", sa.Integer(), nullable=False),
        sa.Column("mapping_type", sa.String(length=50), nullable=True),
        sa.Column("execution_dependency", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["opportunity_id"], ["service_opportunities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["practice_id"], ["service_practices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("service_opportunity_practice_mapping")
    op.drop_table("service_past_deals")
    op.drop_table("service_practices")
    op.drop_table("service_opportunities")
    op.drop_table("service_technologies")
    op.drop_index(op.f("ix_service_companies_company_name"), table_name="service_companies")
    op.drop_table("service_companies")
