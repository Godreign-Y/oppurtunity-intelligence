"""Mutable context accumulated while a post moves through the pipeline."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineContext(BaseModel):
    """Per-run and per-post context for downstream stages."""

    run_id: UUID
    accumulated: dict[str, Any] = Field(default_factory=dict)

    def merge_metadata(self, metadata: dict[str, Any]) -> None:
        """Merge stage metadata into accumulated context."""
        self.accumulated.update(metadata)
