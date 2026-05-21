from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class IngestionErrorRecord:
    error_id: str
    run_id: str
    error_type: str
    message: str
    retryable: bool
    occurred_at: datetime | None = None
    metadata: dict[str, object] = field(default_factory=dict)
