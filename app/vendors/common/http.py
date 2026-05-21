from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol


@dataclass(frozen=True)
class RequestMetadata:
    method: str
    url: str
    timeout_seconds: float
    headers: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ResponseMetadata:
    status_code: int
    elapsed_seconds: float
    headers: dict[str, str] = field(default_factory=dict)
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class HttpClient(Protocol):
    def request(self, metadata: RequestMetadata) -> ResponseMetadata:
        ...
