from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.vendors.common.http import HttpClient


@dataclass(frozen=True)
class FredClientConfig:
    api_key: str | None = None
    base_url: str = "https://api.stlouisfed.org"
    timeout_seconds: float = 30.0


class FredClient(Protocol):
    def fetch_series_observations(self, series_id: str) -> list[dict[str, object]]:
        ...

    def fetch_series_metadata(self, series_id: str) -> dict[str, object]:
        ...


class UnsupportedFredClient:
    def __init__(self, config: FredClientConfig, http_client: HttpClient | None = None) -> None:
        self.config = config
        self.http_client = http_client

    def fetch_series_observations(self, series_id: str) -> list[dict[str, object]]:
        raise NotImplementedError("FRED client fetch is not implemented yet.")

    def fetch_series_metadata(self, series_id: str) -> dict[str, object]:
        raise NotImplementedError("FRED client fetch is not implemented yet.")
