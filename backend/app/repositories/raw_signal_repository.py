from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.raw_signal import RawSignal

def get_by_source_and_external_id(
    session: Session,
    source: str,
    external_id: str,
):
    stmt = select(RawSignal).where(
        RawSignal.source == source,
        RawSignal.external_id == external_id,
    )
    result = session.execute(stmt)
    return result.scalar_one_or_none()


class RawSignalRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict):
        query = select(RawSignal).where(
            RawSignal.external_id == data["external_id"]
        )
        result = self.db.execute(query)
        existing = result.scalars().first()

        if existing:
            return  # skip duplicate

        self.db.add(RawSignal(**data))
        self.db.commit()