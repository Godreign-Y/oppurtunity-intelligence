"""Retrieve and export validated intelligence records."""

from uuid import UUID

from redit.models.intelligence import IntelligenceRecord
from redit.storage.base import RunStore


class IntelligenceService:
    """Read-only access to stored intelligence for a run."""

    def __init__(self, run_store: RunStore) -> None:
        """Attach run store."""
        self._run_store = run_store

    async def get_records(self, run_id: UUID) -> list[IntelligenceRecord] | None:
        """
        Return intelligence records for a run.

        Returns None when the run_id does not exist.
        """
        run = await self._run_store.get_run(run_id)
        if run is None:
            return None
        return await self._run_store.get_intelligence(run_id)

    async def export_records(self, run_id: UUID) -> list[dict] | None:
        """Return JSON-serializable intelligence payloads for export."""
        records = await self.get_records(run_id)
        if records is None:
            return None
        return [r.model_dump(mode="json") for r in records]
