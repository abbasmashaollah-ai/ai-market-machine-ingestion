from __future__ import annotations

from typing import Protocol

from app.ingestion.backfill.planner import BackfillRequest


class BackfillJobRunner(Protocol):
    def run_batch(self, request: BackfillRequest, batch: object) -> None:
        ...
