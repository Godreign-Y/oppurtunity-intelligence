from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Company, FundingEvent
from src.schemas.funding import CompanyCreate, FundingEventCreate

async def get_company_by_name(session: AsyncSession, name: str) -> Optional[Company]:
    result = await session.execute(select(Company).where(Company.name == name))
    return result.scalars().first()

async def create_company(session: AsyncSession, company_data: CompanyCreate) -> Company:
    new_company = Company(
        name=company_data.name,
        industry=company_data.industry,
        is_product_based=company_data.is_product_based,
        description=company_data.description
    )
    session.add(new_company)
    await session.commit()
    await session.refresh(new_company)
    return new_company

async def create_funding_event(session: AsyncSession, event_data: FundingEventCreate, company_id: int) -> FundingEvent:
    new_event = FundingEvent(
        company_id=company_id,
        amount=event_data.amount,
        stage=event_data.stage,
        source_url=event_data.source_url,
        raw_text=event_data.raw_text,
        opportunity_score=event_data.opportunity_score
    )
    session.add(new_event)
    await session.commit()
    await session.refresh(new_event)
    return new_event

async def get_recent_funding_events(session: AsyncSession, limit: int = 50) -> List[FundingEvent]:
    result = await session.execute(
        select(FundingEvent).order_by(FundingEvent.date.desc()).limit(limit)
    )
    return list(result.scalars().all())
