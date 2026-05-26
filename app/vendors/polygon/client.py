from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.vendors.common.http import HttpClient, HttpResponse, RequestMetadata
from app.vendors.polygon.endpoints import (
    daily_aggregates_params,
    daily_aggregates_path,
    reference_tickers_params,
    reference_tickers_path,
    ticker_details_path,
)
from app.vendors.polygon.rate_limiter import PolygonRateLimiter
from app.vendors.polygon.retry import RetryPolicy, build_retry_policy


@dataclass(frozen=True)
class PolygonClientConfig:
    api_key: str | None = None
    base_url: str = "https://api.polygon.io"
    timeout_seconds: float = 30.0


class PolygonClient(Protocol):
    def fetch_aggregates_raw(
        self,
        ticker: str,
        from_date: str,
        to_date: str,
        *,
        adjusted: bool = True,
    ) -> list[dict[str, object]]:
        ...

    def fetch_tickers_raw(self) -> list[dict[str, object]]:
        ...

    def fetch_ticker_raw(self, ticker: str) -> dict[str, object]:
        ...


class UnsupportedPolygonClient:
    def __init__(
        self,
        config: PolygonClientConfig,
        http_client: HttpClient | None = None,
        *,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: PolygonRateLimiter | None = None,
    ) -> None:
        self.config = config
        self.http_client = http_client
        self.retry_policy = retry_policy or build_retry_policy()
        self.rate_limiter = rate_limiter

    def fetch_aggregates_raw(
        self,
        ticker: str,
        from_date: str,
        to_date: str,
        *,
        adjusted: bool = True,
    ) -> list[dict[str, object]]:
        if self.http_client is None:
            raise NotImplementedError("Polygon client transport is not configured.")
        self._acquire_rate_limit()
        request_metadata = RequestMetadata(
            method="GET",
            url=self._build_url(daily_aggregates_path(ticker, from_date, to_date)),
            timeout_seconds=self.config.timeout_seconds,
            query_params=daily_aggregates_params(self.config.api_key, adjusted=adjusted),
        )
        response = self.http_client.request(request_metadata)
        return self._extract_raw_list(response)

    def fetch_tickers_raw(self) -> list[dict[str, object]]:
        if self.http_client is None:
            raise NotImplementedError("Polygon client transport is not configured.")
        self._acquire_rate_limit()
        request_metadata = RequestMetadata(
            method="GET",
            url=self._build_url(reference_tickers_path()),
            timeout_seconds=self.config.timeout_seconds,
            query_params=reference_tickers_params(self.config.api_key),
        )
        response = self.http_client.request(request_metadata)
        return self._extract_raw_list(response)

    def fetch_ticker_raw(self, ticker: str) -> dict[str, object]:
        if self.http_client is None:
            raise NotImplementedError("Polygon client transport is not configured.")
        self._acquire_rate_limit()
        request_metadata = RequestMetadata(
            method="GET",
            url=self._build_url(ticker_details_path(ticker)),
            timeout_seconds=self.config.timeout_seconds,
            query_params={"apiKey": self.config.api_key} if self.config.api_key is not None else {},
        )
        response = self.http_client.request(request_metadata)
        payload = response.json
        return payload if isinstance(payload, dict) else {}

    def fetch_tickers_filtered_raw(self, *, active: bool | None = None, limit: int | None = None) -> list[dict[str, object]]:
        if self.http_client is None:
            raise NotImplementedError("Polygon client transport is not configured.")
        self._acquire_rate_limit()
        request_metadata = RequestMetadata(
            method="GET",
            url=self._build_url(reference_tickers_path()),
            timeout_seconds=self.config.timeout_seconds,
            query_params=reference_tickers_params(self.config.api_key, active=active, limit=limit),
        )
        response = self.http_client.request(request_metadata)
        return self._extract_raw_list(response)

    def fetch_aggregates(self, ticker: str, from_date: str, to_date: str) -> list[dict[str, object]]:
        return self.fetch_aggregates_raw(ticker, from_date, to_date)

    def fetch_tickers(self) -> list[dict[str, object]]:
        return self.fetch_tickers_raw()

    def _build_url(self, path: str) -> str:
        return f"{self.config.base_url.rstrip('/')}{path}"

    def _acquire_rate_limit(self) -> None:
        if self.rate_limiter is not None:
            self.rate_limiter.acquire()

    def _extract_raw_list(self, response: HttpResponse) -> list[dict[str, object]]:
        payload = response.json
        if isinstance(payload, dict) and "results" in payload and isinstance(payload["results"], list):
            return payload["results"]
        if isinstance(payload, list):
            return payload
        return []


def build_polygon_http_client(base_url: str = "https://api.polygon.io") -> HttpClient:
    from app.vendors.common.http import UrlLibHttpClient

    return UrlLibHttpClient()


def build_polygon_client(config: PolygonClientConfig, http_client: HttpClient | None = None) -> UnsupportedPolygonClient:
    return UnsupportedPolygonClient(config, http_client=http_client or build_polygon_http_client(config.base_url))
