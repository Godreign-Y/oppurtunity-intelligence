"""
Normalization service using github_signals.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.github_signal import GitHubSignal
from app.models.normalized_signal import NormalizedSignal

from app.normalization.rules import (
    classify_signal,
    detect_ecosystem,
    detect_severity,
    calculate_confidence,
)


class NormalizationService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self):

        result = await self.db.execute(select(GitHubSignal))
        github_signals = result.scalars().all()

        for gh in github_signals:

            # ✅ Avoid duplicate normalization
            exists_query = select(NormalizedSignal).where(
                NormalizedSignal.github_signal_id == gh.id
            )
            existing = (await self.db.execute(exists_query)).scalars().first()

            if existing:
                continue

            text = f"{gh.title} {gh.content}"

            normalized = NormalizedSignal(
                github_signal_id=gh.id,
                signal_type=classify_signal(text),
                severity=detect_severity(text),
                ecosystem=detect_ecosystem(text),
                confidence=calculate_confidence(text),
            )

            self.db.add(normalized)

        await self.db.commit()