from sqlalchemy import select
from app.models.raw_signal import RawSignal
from sqlalchemy import select
from app.models.raw_signal import RawSignal


async def get_by_source_and_external_id(
    session,
    source: str,
    external_id: str,
):
    stmt = select(RawSignal).where(
        RawSignal.source == source,
        RawSignal.external_id == external_id,
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()

class RawSignalRepository:

    def __init__(self, db):
        self.db = db

    async def create(self, data: dict):

        query = select(RawSignal).where(
            RawSignal.external_id == data["external_id"]
        )

        result = await self.db.execute(query)
        existing = result.scalars().first()

        if existing:
            return  # ✅ skip duplicate

        self.db.add(RawSignal(**data))
        await self.db.commit()