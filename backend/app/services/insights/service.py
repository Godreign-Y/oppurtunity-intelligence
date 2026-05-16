"""
Insight generation service.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.normalized_signal import NormalizedSignal
from app.models.github_signal import GitHubSignal


class InsightService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ✅ 1. Most common signal types
    async def top_signal_types(self):
        query = (
            select(
                NormalizedSignal.signal_type,
                func.count().label("count")
            )
            .group_by(NormalizedSignal.signal_type)
            .order_by(func.count().desc())
        )

        result = await self.db.execute(query)
        return result.all()

    # ✅ 2. Ecosystem analysis
    async def ecosystem_distribution(self):
        query = (
            select(
                NormalizedSignal.ecosystem,
                func.count().label("count")
            )
            .group_by(NormalizedSignal.ecosystem)
        )

        result = await self.db.execute(query)
        return result.all()

    # ✅ 3. Severity breakdown
    async def severity_distribution(self):
        query = (
            select(
                NormalizedSignal.severity,
                func.count().label("count")
            )
            .group_by(NormalizedSignal.severity)
        )

        result = await self.db.execute(query)
        return result.all()

    # ✅ 4. Top companies facing issues (VERY IMPORTANT)
    async def top_orgs(self):
        query = (
            select(
                GitHubSignal.metadata_json["org"].as_string().label("org"),
                func.count().label("count")
            )
            .join(
                NormalizedSignal,
                NormalizedSignal.github_signal_id == GitHubSignal.id
            )
            .group_by("org")
            .order_by(func.count().desc())
        )

        result = await self.db.execute(query)
        return result.all()

    # ✅ 5. High severity orgs (consulting leads)
    async def high_severity_orgs(self):
        query = (
            select(
                GitHubSignal.metadata_json["org"].as_string().label("org"),
                func.count().label("count")
            )
            .join(
                NormalizedSignal,
                NormalizedSignal.github_signal_id == GitHubSignal.id
            )
            .where(NormalizedSignal.severity == "high")
            .group_by("org")
            .order_by(func.count().desc())
        )

        result = await self.db.execute(query)
        return result.all()