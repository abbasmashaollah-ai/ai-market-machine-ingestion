from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.vendors.common.http import HttpClient, RequestMetadata, ResponseMetadata


@dataclass(frozen=True)
class PolygonClientConfig:
    api_key: str | None = None
    base_url: str = "https://api.polygon.io"
    timeout_seconds: float = 30.0


class PolygonClient(Protocol):
    def fetch_aggregates(self, ticker: str, from_date: str, to_date: str) -> list[dict[str, object]]:
        ...

    def fetch_tickers(self) -> list[dict[str, object]]:
        ...


class UnsupportedPolygonClient:
    def __init__(self, config: PolygonClientConfig, http_client: HttpClient | None = None) -> None:
        self.config = config
        self.http_client = http_client

    def fetch_aggregates(self, ticker: str, from_date: str, to_date: str) -> list[dict[str, object]]:
        raise NotImplementedError("Polygon client fetch is not implemented yet.")

    def fetch_tickers(self) -> list[dict[str, object]]:
        raise NotImplementedError("Polygon client fetch is not implemented yet.")


def build_request_metadata(url: str, *, timeout_seconds: float) -> RequestMetadata:
    return RequestMetadata(method="GET", url=url, timeout_seconds=timeout_seconds)
