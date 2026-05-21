from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.vendors.common.http import HttpClient, HttpResponse, RequestMetadata
from app.vendors.fred.endpoints import (
    series_metadata_params,
    series_metadata_path,
    series_observations_path,
    series_observations_query,
)


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

    def fetch_series_observations_raw(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[dict[str, object]]:
        if self.http_client is None:
            raise NotImplementedError("FRED client transport is not configured.")
        request_metadata = RequestMetadata(
            method="GET",
            url=self._build_url(series_observations_path(series_id)),
            timeout_seconds=self.config.timeout_seconds,
            query_params=series_observations_query(
                self.config.api_key,
                observation_start=observation_start,
                observation_end=observation_end,
            ),
        )
        response = self.http_client.request(request_metadata)
        return self._extract_raw_list(response)

    def fetch_series_metadata_raw(self, series_id: str) -> dict[str, object]:
        if self.http_client is None:
            raise NotImplementedError("FRED client transport is not configured.")
        request_metadata = RequestMetadata(
            method="GET",
            url=self._build_url(series_metadata_path(series_id)),
            timeout_seconds=self.config.timeout_seconds,
            query_params=series_metadata_params(self.config.api_key),
        )
        response = self.http_client.request(request_metadata)
        return self._extract_raw_dict(response)

    def fetch_series_observations(self, series_id: str) -> list[dict[str, object]]:
        return self.fetch_series_observations_raw(series_id)

    def fetch_series_metadata(self, series_id: str) -> dict[str, object]:
        return self.fetch_series_metadata_raw(series_id)

    def _build_url(self, path: str) -> str:
        return f"{self.config.base_url.rstrip('/')}{path}"

    def _extract_raw_list(self, response: HttpResponse) -> list[dict[str, object]]:
        payload = response.json
        if isinstance(payload, dict) and "observations" in payload and isinstance(payload["observations"], list):
            return payload["observations"]
        if isinstance(payload, list):
            return payload
        return []

    def _extract_raw_dict(self, response: HttpResponse) -> dict[str, object]:
        payload = response.json
        if isinstance(payload, dict):
            return payload
        return {}
