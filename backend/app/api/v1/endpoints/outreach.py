"""Outreach recommendation endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.outreach.service import list_outreach_recommendations

router = APIRouter()


@router.get("/recommendations")
async def get_outreach_recommendations(
    company_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[dict]:
    return await list_outreach_recommendations(db, company_name=company_name)
