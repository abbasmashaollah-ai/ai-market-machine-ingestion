from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol
import re

from app.vendors.common.errors import VendorHttpStatusError, VendorTimeoutError, VendorUnavailableError
from app.vendors.common.http import HttpClient, HttpResponse, RequestMetadata, UrlLibHttpClient


class FmpFetchErrorKind(str, Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    INVALID_RESPONSE = "invalid_response"


@dataclass(frozen=True)
class FmpFetchError(Exception):
    kind: FmpFetchErrorKind
    message: str
    retryable: bool = False

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class FmpClientConfig:
    api_key: str | None = None
    base_url: str = "https://financialmodelingprep.com"
    timeout_seconds: float = 30.0
    retry_attempts: int = 2


class FmpOhlcvClient(Protocol):
    def fetch_historical_ohlcv_raw(self, symbol: str, *, start_date: str, end_date: str) -> list[dict[str, object]]:
        ...


class UnsupportedFmpClient:
    def __init__(self, config: FmpClientConfig, http_client: HttpClient | None = None) -> None:
        self.config = config
        self.http_client = http_client

    def fetch_historical_ohlcv_raw(self, symbol: str, *, start_date: str, end_date: str) -> list[dict[str, object]]:
        if self.http_client is None:
            raise NotImplementedError("FMP client transport is not configured.")
        request_metadata = RequestMetadata(
            method="GET",
            url=self._build_url(symbol),
            timeout_seconds=self.config.timeout_seconds,
            query_params=self._query_params(start_date=start_date, end_date=end_date),
        )
        attempts = max(int(self.config.retry_attempts), 1)
        last_error: FmpFetchError | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = self.http_client.request(request_metadata)
                return self._extract_historical(response)
            except (VendorTimeoutError, VendorUnavailableError, VendorHttpStatusError) as exc:
                last_error = self._classify_http_error(exc)
                if not last_error.retryable or attempt >= attempts:
                    raise last_error from exc
            except FmpFetchError as exc:
                last_error = exc
                if not exc.retryable or attempt >= attempts:
                    raise
        if last_error is not None:
            raise last_error
        raise FmpFetchError(FmpFetchErrorKind.INVALID_RESPONSE, "FMP request failed unexpectedly.")

    def _build_url(self, symbol: str) -> str:
        return f"{self.config.base_url.rstrip('/')}/api/v3/historical-price-full/{symbol}"

    def _query_params(self, *, start_date: str, end_date: str) -> dict[str, str]:
        params = {"from": start_date, "to": end_date}
        if self.config.api_key is not None:
            params["apikey"] = self.config.api_key
        return params

    def _classify_http_error(self, exc: Exception) -> FmpFetchError:
        message = str(exc) or "FMP request failed"
        if isinstance(exc, VendorTimeoutError):
            return FmpFetchError(FmpFetchErrorKind.TRANSIENT, message, retryable=True)
        if isinstance(exc, VendorUnavailableError):
            return FmpFetchError(FmpFetchErrorKind.TRANSIENT, message, retryable=True)
        if isinstance(exc, VendorHttpStatusError):
            status_code = self._status_code_from_message(message)
            retryable = status_code is not None and status_code >= 500
            kind = FmpFetchErrorKind.TRANSIENT if retryable else FmpFetchErrorKind.PERMANENT
            return FmpFetchError(kind, message, retryable=retryable)
        return FmpFetchError(FmpFetchErrorKind.PERMANENT, message, retryable=False)

    def _status_code_from_message(self, message: str) -> int | None:
        match = re.search(r"(\d{3})", message)
        if match is None:
            return None
        try:
            return int(match.group(1))
        except ValueError:
            return None

    def _extract_historical(self, response: HttpResponse) -> list[dict[str, object]]:
        payload = response.json
        if isinstance(payload, dict):
            if "historical" in payload and isinstance(payload["historical"], list):
                return [row for row in payload["historical"] if isinstance(row, dict)]
            if "results" in payload and isinstance(payload["results"], list):
                return [row for row in payload["results"] if isinstance(row, dict)]
            raise FmpFetchError(
                FmpFetchErrorKind.INVALID_RESPONSE,
                "FMP response payload did not include a historical record list.",
                retryable=False,
            )
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        raise FmpFetchError(
            FmpFetchErrorKind.INVALID_RESPONSE,
            "FMP response payload was not parseable as JSON.",
            retryable=False,
        )


def build_fmp_http_client(base_url: str = "https://financialmodelingprep.com") -> HttpClient:
    return UrlLibHttpClient()


def build_fmp_client(config: FmpClientConfig, http_client: HttpClient | None = None) -> UnsupportedFmpClient:
    return UnsupportedFmpClient(config, http_client=http_client or build_fmp_http_client(config.base_url))
