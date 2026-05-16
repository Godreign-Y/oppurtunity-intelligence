"""
Repository for GitHub signals.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.github_signal import GitHubSignal


class GitHubSignalRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict):

        query = select(GitHubSignal).where(
            GitHubSignal.external_id == data["external_id"]
        )

        result = await self.db.execute(query)
        existing = result.scalars().first()

        if existing:
            return

        self.db.add(GitHubSignal(**data))
        await self.db.commit()