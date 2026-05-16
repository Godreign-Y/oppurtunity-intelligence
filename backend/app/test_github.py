import asyncio
from app.core.database import AsyncSessionLocal
from app.services.github.service import GitHubIngestionService

queries = [
    "deployment failed",
    "rollback issue",
    "latency issue",
    "outage",
]
async def test():
    async with AsyncSessionLocal() as db:
        service = GitHubIngestionService(db)
        for q in queries:
            result = await service.ingest(q)
            print(q, len(result))

        print(len(result))


asyncio.run(test())