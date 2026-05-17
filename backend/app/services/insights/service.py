"""
Insight generation service — synchronous version.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, String

from app.models.normalized_signal import NormalizedSignal
from app.models.github_signal import GitHubSignal


class InsightService:

    def __init__(self, db: Session):
        self.db = db

    # 1. Most common signal types
    def top_signal_types(self):
        query = (
            select(
                NormalizedSignal.signal_type,
                func.count().label("count")
            )
            .group_by(NormalizedSignal.signal_type)
            .order_by(func.count().desc())
        )
        result = self.db.execute(query)
        return [{"signal_type": row[0], "count": row[1]} for row in result.all()]

    # 2. Ecosystem analysis
    def ecosystem_distribution(self):
        query = (
            select(
                NormalizedSignal.ecosystem,
                func.count().label("count")
            )
            .group_by(NormalizedSignal.ecosystem)
        )
        result = self.db.execute(query)
        return [{"ecosystem": row[0], "count": row[1]} for row in result.all()]

    # 3. Severity breakdown
    def severity_distribution(self):
        query = (
            select(
                NormalizedSignal.severity,
                func.count().label("count")
            )
            .group_by(NormalizedSignal.severity)
        )
        result = self.db.execute(query)
        return [{"severity": row[0], "count": row[1]} for row in result.all()]

    # 4. Top orgs facing issues (consulting leads)
    def top_orgs(self):
        query = (
            select(
                cast(GitHubSignal.metadata_json["org"], String).label("org"),
                func.count().label("count")
            )
            .join(
                NormalizedSignal,
                NormalizedSignal.github_signal_id == GitHubSignal.id
            )
            .group_by("org")
            .order_by(func.count().desc())
        )
        result = self.db.execute(query)
        return [{"org": str(row[0]).strip('"'), "count": row[1]} for row in result.all() if row[0]]

    # 5. High severity orgs
    def high_severity_orgs(self):
        query = (
            select(
                cast(GitHubSignal.metadata_json["org"], String).label("org"),
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
        result = self.db.execute(query)
        return [{"org": str(row[0]).strip('"'), "count": row[1]} for row in result.all() if row[0]]

    # 6. Recent GitHub signals (for dashboard display)
    def recent_github_signals(self, limit: int = 50):
        query = (
            select(GitHubSignal)
            .order_by(GitHubSignal.created_at.desc())
            .limit(limit)
        )
        result = self.db.execute(query)
        signals = result.scalars().all()
        return [
            {
                "id": s.id,
                "external_id": s.external_id,
                "title": s.title,
                "content": s.content[:300] if s.content else "",
                "source_url": s.source_url,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "org": (s.metadata_json or {}).get("org"),
                "repo": (s.metadata_json or {}).get("repo"),
                "comments": (s.metadata_json or {}).get("comments"),
                "labels": (s.metadata_json or {}).get("labels", []),
                "query": (s.metadata_json or {}).get("query"),
            }
            for s in signals
        ]

    # 7. Normalized signals summary
    def normalized_signals_summary(self, limit: int = 50):
        query = (
            select(NormalizedSignal, GitHubSignal)
            .join(GitHubSignal, NormalizedSignal.github_signal_id == GitHubSignal.id)
            .order_by(NormalizedSignal.confidence.desc())
            .limit(limit)
        )
        result = self.db.execute(query)
        rows = result.all()
        return [
            {
                "id": ns.id,
                "signal_type": ns.signal_type,
                "severity": ns.severity,
                "ecosystem": ns.ecosystem,
                "confidence": ns.confidence,
                "title": gh.title,
                "source_url": gh.source_url,
                "org": (gh.metadata_json or {}).get("org"),
                "repo": (gh.metadata_json or {}).get("repo"),
                "created_at": gh.created_at.isoformat() if gh.created_at else None,
            }
            for ns, gh in rows
        ]