from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class VendorPayloadMetadata:
    vendor: str
    source: str | None = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str | None = None
    correlation_id: str | None = None
    content_type: str | None = None
    payload_version: str | None = None
