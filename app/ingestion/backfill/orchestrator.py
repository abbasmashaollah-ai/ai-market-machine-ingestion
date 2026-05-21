from __future__ import annotations

from typing import Protocol

from app.ingestion.backfill.planner import BackfillRequest


class BackfillOrchestrator(Protocol):
    def plan(self, request: BackfillRequest) -> list[object]:
        ...

    def run(self, request: BackfillRequest) -> None:
        ...
