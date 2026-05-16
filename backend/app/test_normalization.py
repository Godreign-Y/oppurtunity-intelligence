import asyncio

from app.core.database import AsyncSessionLocal
from app.services.normalization.service import NormalizationService


async def test():
    async with AsyncSessionLocal() as db:
        service = NormalizationService(db)
        await service.run()
        print("Normalization complete ✅")


if __name__ == "__main__":
    asyncio.run(test())