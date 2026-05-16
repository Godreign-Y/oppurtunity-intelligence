import asyncio

from app.core.database import AsyncSessionLocal
from app.services.insights.service import InsightService


async def test():
    async with AsyncSessionLocal() as db:
        service = InsightService(db)

        print("\nTop Signal Types:")
        print(await service.top_signal_types())

        print("\nEcosystem Distribution:")
        print(await service.ecosystem_distribution())

        print("\nSeverity Distribution:")
        print(await service.severity_distribution())

        print("\nTop Organizations:")
        print(await service.top_orgs())

        print("\nHigh Severity Organizations:")
        print(await service.high_severity_orgs())


if __name__ == "__main__":
    asyncio.run(test())