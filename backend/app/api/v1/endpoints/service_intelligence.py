"""Relanto service-company intelligence endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.service_intelligence.relanto_seed import seed_relanto
from app.services.service_intelligence.service import list_practices, list_relanto_opportunities

router = APIRouter()


@router.post("/seed/relanto")
def seed_relanto_endpoint(db: Session = Depends(get_db)) -> dict:
    company = seed_relanto(db)
    return {"status": "success", "company_name": company.company_name}


@router.get("/practices")
def get_practices(db: Session = Depends(get_db)) -> list[dict]:
    return list_practices(db)


@router.get("/opportunities")
def get_relanto_opportunities(
    company_name: str | None = Query(default=None),
    practice_code: str | None = Query(default=None),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[dict]:
    return list_relanto_opportunities(
        db,
        company_name=company_name,
        practice_code=practice_code,
        refresh=refresh,
    )
