"""Abstract storage for pipeline run state."""

from abc import ABC, abstractmethod
from uuid import UUID

from redit.models.intelligence import IntelligenceRecord
from redit.models.pipeline import IngestionRunSummary


class RunStore(ABC):
    """Interface for ingestion run and intelligence persistence."""

    @abstractmethod
    async def create_run(self, summary: IngestionRunSummary) -> None:
        """Persist a new run record."""

    @abstractmethod
    async def update_run(self, summary: IngestionRunSummary) -> None:
        """Update run progress or completion."""

    @abstractmethod
    async def get_run(self, run_id: UUID) -> IngestionRunSummary | None:
        """Fetch run by id."""

    @abstractmethod
    async def append_intelligence(self, run_id: UUID, record: IntelligenceRecord) -> None:
        """Store validated intelligence for a passed post."""

    @abstractmethod
    async def get_intelligence(self, run_id: UUID) -> list[IntelligenceRecord]:
        """Return intelligence records for a run."""
