"""
Repository for GitHub signals.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.github_signal import GitHubSignal


class GitHubSignalRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict):

        query = select(GitHubSignal).where(
            GitHubSignal.external_id == data["external_id"]
        )

        result = self.db.execute(query)
        existing = result.scalars().first()

        if existing:
            return

        self.db.add(GitHubSignal(**data))
        self.db.commit()
