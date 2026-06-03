"""Read-only client for certified evidence served by ai-market-machine-data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.vendors.common.http import HttpClient, HttpResponse, RequestMetadata, UrlLibHttpClient


class DataReadClientError(Exception):
    """Base error for data-read client failures."""


class DataReadClientAuthError(DataReadClientError):
    """Raised when the read service rejects authentication."""


class DataReadClientResponseError(DataReadClientError):
    """Raised for non-2xx or malformed responses."""


class DataReadClientTimeoutError(DataReadClientError):
    """Raised when the read request times out."""


@dataclass(frozen=True, slots=True)
class DataReadClientConfig:
    base_url: str
    ops_internal_token: str
    timeout_seconds: float = 30.0
    max_retries: int = 0

    def __post_init__(self) -> None:
        normalized_base_url = self.base_url.strip().rstrip("/")
        if not normalized_base_url:
            raise ValueError("base_url is required")
        if not self.ops_internal_token or not str(self.ops_internal_token).strip():
            raise ValueError("ops_internal_token is required")
        object.__setattr__(self, "base_url", normalized_base_url)
        object.__setattr__(self, "ops_internal_token", str(self.ops_internal_token).strip())


class DataReadTransport(Protocol):
    def request(self, metadata: RequestMetadata) -> HttpResponse:
        ...


class DataReadClient:
    """Read-only GET client for certified warehouse evidence.

    The endpoint path is intentionally conservative and repository-local:
    /private-read/canonical_ohlcv/certified-history
    """

    def __init__(self, config: DataReadClientConfig, http_client: DataReadTransport | None = None) -> None:
        self.config = config
        self._http_client = http_client or UrlLibHttpClient()

    def __repr__(self) -> str:  # pragma: no cover - defensive formatting only
        return f"DataReadClient(base_url={self.config.base_url!r}, timeout_seconds={self.config.timeout_seconds!r}, max_retries={self.config.max_retries!r})"

    def get_symbol_ohlcv_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        order: str = "asc",
    ) -> dict[str, object]:
        normalized_symbol = self._normalize_symbol(symbol)
        if not normalized_symbol:
            raise DataReadClientResponseError("symbol is required")

        request_metadata = RequestMetadata(
            method="GET",
            url=f"{self.config.base_url}/internal/read/symbol/{normalized_symbol}/ohlcv/history",
            timeout_seconds=self.config.timeout_seconds,
            headers={
                "X-Ops-Internal-Token": self.config.ops_internal_token,
                "Accept": "application/json",
            },
            query_params=self._symbol_query_params(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                order=order,
            ),
        )

        return self._request_and_parse_object(request_metadata)

    def get_certified_ohlcv_history(
        self,
        symbols: list[str] | tuple[str, ...] | set[str],
        start_date: str | None = None,
        end_date: str | None = None,
        lookback_days: int | None = None,
    ) -> list[dict[str, object]]:
        if not symbols:
            raise DataReadClientResponseError("symbols are required")

        normalized_symbols = [self._normalize_symbol(symbol) for symbol in symbols]
        if any(not symbol for symbol in normalized_symbols):
            raise DataReadClientResponseError("symbols must be non-empty strings")

        combined_rows: list[dict[str, object]] = []
        for symbol in normalized_symbols:
            payload = self.get_symbol_ohlcv_history(
                symbol,
                start_date=start_date,
                end_date=end_date,
                limit=lookback_days,
                order="asc",
            )
            combined_rows.extend(self._extract_historical_ohlcv(payload))
        return combined_rows

    def _normalize_symbol(self, symbol: object) -> str:
        return str(symbol).strip().upper()

    def _query_params(
        self,
        symbols: list[str],
        *,
        start_date: str | None,
        end_date: str | None,
        lookback_days: int | None,
    ) -> dict[str, str]:
        params = {"symbols": ",".join(symbols)}
        if start_date is not None:
            params["start_date"] = str(start_date)
        if end_date is not None:
            params["end_date"] = str(end_date)
        if lookback_days is not None:
            params["lookback_days"] = str(int(lookback_days))
        return params

    def _symbol_query_params(
        self,
        *,
        start_date: str | None,
        end_date: str | None,
        limit: int | None,
        order: str,
    ) -> dict[str, str]:
        params: dict[str, str] = {}
        if start_date is not None:
            params["start_date"] = str(start_date)
        if end_date is not None:
            params["end_date"] = str(end_date)
        if limit is not None:
            params["limit"] = str(int(limit))
        if order:
            params["order"] = str(order).strip().lower()
        return params

    def _request_and_parse_object(self, request_metadata: RequestMetadata) -> dict[str, object]:
        attempts = max(int(self.config.max_retries), 0) + 1
        last_error: DataReadClientError | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = self._http_client.request(request_metadata)
                return self._parse_object_response(response)
            except DataReadClientTimeoutError as exc:
                last_error = exc
                if attempt >= attempts:
                    raise
            except DataReadClientError as exc:
                last_error = exc
                if attempt >= attempts:
                    raise
        if last_error is not None:
            raise last_error
        raise DataReadClientResponseError("data read request failed unexpectedly")

    def _parse_object_response(self, response: HttpResponse) -> dict[str, object]:
        status_code = int(getattr(response, "status_code", getattr(response.metadata, "status_code", 0)))
        if status_code in (401, 403):
            raise DataReadClientAuthError(f"data read auth failed with status {status_code}")
        if status_code < 200 or status_code >= 300:
            raise DataReadClientResponseError(f"unexpected data read status {status_code}")

        payload = response.json
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, list):
            return {"historical_ohlcv": [row for row in payload if isinstance(row, dict)]}
        raise DataReadClientResponseError("data read response had an invalid shape")

    def _extract_rows(self, payload: Any) -> list[dict[str, object]] | None:
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict):
            for key in ("rows", "results", "data", "historical", "historical_ohlcv"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
            return None
        return None

    def _extract_historical_ohlcv(self, payload: Any) -> list[dict[str, object]]:
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict):
            for key in ("historical_ohlcv", "rows", "results", "data", "historical", "ohlcv"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
            raise DataReadClientResponseError("data read response had an invalid shape")
        raise DataReadClientResponseError("data read response had an invalid shape")
