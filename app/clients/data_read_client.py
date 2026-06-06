"""Read-only client for certified evidence served by ai-market-machine-data."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol
from typing import Any


@dataclass(frozen=True, slots=True)
class RequestMetadata:
    method: str
    url: str
    timeout_seconds: float
    headers: dict[str, str]
    query_params: dict[str, str]


@dataclass(frozen=True, slots=True)
class ResponseMetadata:
    status_code: int
    elapsed_seconds: float = 0.0


@dataclass(frozen=True, slots=True)
class HttpResponse:
    metadata: ResponseMetadata
    text: str
    json: Any | None = None


class HttpClient(Protocol):
    def request(self, metadata: RequestMetadata) -> HttpResponse:
        ...


class UrlLibHttpClient:
    def request(self, metadata: RequestMetadata) -> HttpResponse:
        raise NotImplementedError("Live transport is not enabled in ai-market-machine")


class DataReadClientError(Exception):
    """Base error for data-read client failures."""


class DataReadClientAuthError(DataReadClientError):
    """Raised when the read service rejects authentication."""


class DataReadClientResponseError(DataReadClientError):
    """Raised for non-2xx or malformed responses."""


class DataReadClientTimeoutError(DataReadClientError):
    """Raised when the read request times out."""


@dataclass(frozen=True, slots=True)
class MarketFeatureBundleReadResult:
    universe: str
    evidence_available: bool
    disabled: bool = False
    unauthorized: bool = False
    route_failure: bool = False
    validation_status: str | None = None
    certification_status: str | None = None
    coverage_status: str | None = None
    quality_status: str | None = None
    missing_data_evidence: tuple[dict[str, object], ...] = ()
    stale_data_evidence: tuple[dict[str, object], ...] = ()
    supported_schema_version: str | None = None
    dataset_version: str | None = None
    schema_version: str | None = None
    compact_summary: dict[str, object] | None = None
    full_bundle_payload: dict[str, object] | None = None
    idempotency_key_prefix: str | None = None
    error_message: str | None = None


def _disabled_market_feature_bundle_result(universe: str, *, error_message: str | None = None) -> MarketFeatureBundleReadResult:
    return MarketFeatureBundleReadResult(
        universe=universe,
        evidence_available=False,
        disabled=True,
        error_message=error_message,
    )


def _redact_sensitive_text(message: str, *, base_url: str | None = None, token: str | None = None) -> str:
    redacted = message
    if base_url:
        redacted = redacted.replace(base_url, "<redacted_base_url>")
    if token:
        redacted = redacted.replace(token, "<redacted_token>")
    return redacted


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

    The live OHLCV history route confirmed for this client is:
    /internal/read/symbol/{symbol}/ohlcv/history
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
        """Fetch certified OHLCV history for one symbol from the live private-read route."""

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
        """Convenience wrapper that combines single-symbol OHLCV history rows."""

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

    @classmethod
    def from_environment(cls, http_client: DataReadTransport | None = None) -> "DataReadClient | None":
        base_url = os.getenv("AI_MARKET_MACHINE_DATA_BASE_URL")
        token = os.getenv("AI_MARKET_MACHINE_DATA_INTERNAL_TOKEN")
        if not base_url or not token:
            return None
        timeout_seconds = float(os.getenv("AI_MARKET_MACHINE_DATA_TIMEOUT_SECONDS", "30"))
        return cls(
            DataReadClientConfig(base_url=base_url, ops_internal_token=token, timeout_seconds=timeout_seconds),
            http_client=http_client,
        )

    @classmethod
    def read_market_feature_bundle_from_environment(
        cls,
        universe: str,
        http_client: DataReadTransport | None = None,
    ) -> MarketFeatureBundleReadResult:
        client = cls.from_environment(http_client=http_client)
        if client is None:
            return _disabled_market_feature_bundle_result(str(universe).strip().upper(), error_message="missing configuration")
        return client.get_market_feature_bundle(universe)

    def get_market_feature_bundle(self, universe: str) -> MarketFeatureBundleReadResult:
        normalized_universe = self._normalize_symbol(universe)
        if not normalized_universe:
            return _disabled_market_feature_bundle_result("", error_message="universe is required")

        request_metadata = RequestMetadata(
            method="GET",
            url=f"{self.config.base_url}/internal/read/market-feature-bundle/{normalized_universe}",
            timeout_seconds=self.config.timeout_seconds,
            headers={
                "X-Ops-Internal-Token": self.config.ops_internal_token,
                "Accept": "application/json",
            },
            query_params={},
        )

        try:
            response = self._http_client.request(request_metadata)
        except Exception as exc:
            return _disabled_market_feature_bundle_result(
                normalized_universe,
                error_message=_redact_sensitive_text(
                    str(exc),
                    base_url=self.config.base_url,
                    token=self.config.ops_internal_token,
                ),
            )

        return self._parse_market_feature_bundle_response(normalized_universe, response)

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

    def _parse_market_feature_bundle_response(
        self,
        universe: str,
        response: HttpResponse,
    ) -> MarketFeatureBundleReadResult:
        status_code = int(getattr(response, "status_code", getattr(response.metadata, "status_code", 0)))
        if status_code in (401, 403):
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, unauthorized=True)
        if status_code == 404:
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False)
        if status_code < 200 or status_code >= 300:
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, route_failure=True)

        payload = response.json
        if not isinstance(payload, dict):
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, route_failure=True)

        schema_version = payload.get("schema_version")
        dataset_version = payload.get("dataset_version")
        validation_status = payload.get("validation_status")
        certification_status = payload.get("certification_status")
        coverage_status = payload.get("coverage_status")
        quality_status = payload.get("quality_status")
        missing_data_evidence = payload.get("missing_data_evidence")
        stale_data_evidence = payload.get("stale_data_evidence")
        compact_summary = payload.get("compact_summary")
        full_bundle_payload = payload.get("full_bundle_payload")
        idempotency_key = payload.get("idempotency_key")

        if schema_version != "market_feature_bundle.v1":
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, schema_version=str(schema_version) if schema_version is not None else None)
        if certification_status != "CERTIFIED":
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, schema_version=str(schema_version), certification_status=str(certification_status) if certification_status is not None else None)
        if validation_status != "PASS":
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, schema_version=str(schema_version), validation_status=str(validation_status) if validation_status is not None else None)
        if coverage_status != "COMPLETE":
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, schema_version=str(schema_version), coverage_status=str(coverage_status) if coverage_status is not None else None)
        if quality_status != "PASS":
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, schema_version=str(schema_version), quality_status=str(quality_status) if quality_status is not None else None)
        if missing_data_evidence not in (None, [], {}):
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, schema_version=str(schema_version))
        if stale_data_evidence not in (None, [], {}):
            return MarketFeatureBundleReadResult(universe=universe, evidence_available=False, schema_version=str(schema_version))

        return MarketFeatureBundleReadResult(
            universe=universe,
            evidence_available=True,
            validation_status=str(validation_status) if validation_status is not None else None,
            certification_status=str(certification_status) if certification_status is not None else None,
            coverage_status=str(coverage_status) if coverage_status is not None else None,
            quality_status=str(quality_status) if quality_status is not None else None,
            supported_schema_version="market_feature_bundle.v1",
            dataset_version=str(dataset_version) if dataset_version is not None else None,
            schema_version=str(schema_version) if schema_version is not None else None,
            compact_summary=compact_summary if isinstance(compact_summary, dict) else None,
            full_bundle_payload=full_bundle_payload if isinstance(full_bundle_payload, dict) else None,
            idempotency_key_prefix=(str(idempotency_key)[:12] if isinstance(idempotency_key, str) and idempotency_key else None),
        )

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
