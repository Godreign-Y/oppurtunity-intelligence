"""In-memory run store."""

from uuid import UUID

from redit.models.intelligence import IntelligenceRecord
from redit.models.pipeline import IngestionRunSummary
from redit.storage.base import RunStore


class InMemoryRunStore(RunStore):
    """In-memory store; only validated intelligence is retained."""

    def __init__(self) -> None:
        """Initialize empty stores."""
        self._runs: dict[UUID, IngestionRunSummary] = {}
        self._intelligence: dict[UUID, list[IntelligenceRecord]] = {}

    async def create_run(self, summary: IngestionRunSummary) -> None:
        """Save new run."""
        self._runs[summary.run_id] = summary
        self._intelligence[summary.run_id] = []

    async def update_run(self, summary: IngestionRunSummary) -> None:
        """Overwrite run summary."""
        self._runs[summary.run_id] = summary

    async def get_run(self, run_id: UUID) -> IngestionRunSummary | None:
        """Get run or None."""
        return self._runs.get(run_id)

    async def append_intelligence(self, run_id: UUID, record: IntelligenceRecord) -> None:
        """Append validated intelligence record."""
        if run_id not in self._intelligence:
            self._intelligence[run_id] = []
        self._intelligence[run_id].append(record)

    async def get_intelligence(self, run_id: UUID) -> list[IntelligenceRecord]:
        """Get intelligence records for run."""
        return list(self._intelligence.get(run_id, []))
