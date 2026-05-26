from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from app.normalization.symbol_master import NormalizedSymbolMasterRecord
from app.vendors.polygon.client import PolygonClient, PolygonClientConfig, build_polygon_client


@dataclass(frozen=True)
class PolygonSymbolMasterSourceConfig:
    api_key: str | None = None
    base_url: str = "https://api.polygon.io"
    timeout_seconds: float = 30.0


class PolygonSymbolMasterSource(Protocol):
    def fetch_reference_tickers_raw(self) -> list[dict[str, object]]:
        ...


class PolygonSymbolMasterAdapter:
    def __init__(
        self,
        config: PolygonSymbolMasterSourceConfig,
        client: PolygonClient | None = None,
    ) -> None:
        self.config = config
        self._client = client

    def _client_or_build(self) -> PolygonClient:
        if self._client is not None:
            return self._client
        if not self.config.api_key:
            raise RuntimeError("POLYGON_API_KEY is required for live Polygon symbol-master checks")
        return build_polygon_client(
            PolygonClientConfig(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout_seconds=self.config.timeout_seconds,
            )
        )

    def fetch_reference_tickers_raw(self) -> list[dict[str, object]]:
        try:
            return self._client_or_build().fetch_tickers_raw()
        except Exception as exc:
            raise RuntimeError(_sanitize_error_message(str(exc))) from exc

    def fetch_reference_tickers(
        self,
        *,
        active: bool | None = True,
        limit: int | None = None,
    ) -> list[dict[str, object]]:
        try:
            client = self._client_or_build()
            if hasattr(client, "fetch_tickers_filtered_raw"):
                return client.fetch_tickers_filtered_raw(active=active, limit=limit)  # type: ignore[attr-defined]
            return client.fetch_tickers_raw()
        except Exception as exc:
            raise RuntimeError(_sanitize_error_message(str(exc))) from exc

    def map_reference_ticker(self, payload: dict[str, object]) -> NormalizedSymbolMasterRecord:
        ticker = _safe_text(payload.get("ticker"))
        active = _safe_bool(payload.get("active"))
        delisted = _safe_bool(payload.get("delisted"))
        if active is None and delisted is True:
            active = False
        if active is None and delisted is False:
            active = True
        return NormalizedSymbolMasterRecord(
            symbol=ticker,
            source="polygon_reference",
            vendor="polygon",
            vendor_symbol=ticker,
            asset_type=_normalize_asset_type(payload.get("type")),
            exchange=_safe_text(payload.get("primary_exchange") or payload.get("exchange")),
            name=_safe_text(payload.get("name")),
            currency=_safe_text(payload.get("currency")) or "USD",
            first_seen_at=_normalize_datetime(payload.get("first_seen_at")),
            last_seen_at=_normalize_datetime(payload.get("last_seen_at")),
            active=active,
            normalization_version="polygon.symbol_master.v1",
            quality_status="pass" if active is True else "warn" if active is False else None,
        )

    def build_sample_reference_payloads(self) -> list[dict[str, object]]:
        return [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "active": True,
                "delisted": False,
                "primary_exchange": "XNAS",
                "type": "CS",
                "currency": "USD",
            },
            {
                "ticker": "SPY",
                "name": "SPDR S&P 500 ETF Trust",
                "active": True,
                "delisted": False,
                "primary_exchange": "XASE",
                "type": "ETF",
                "currency": "USD",
            },
            {
                "ticker": "I:VIX",
                "name": "CBOE Volatility Index",
                "active": False,
                "delisted": True,
                "primary_exchange": "XCBO",
                "type": "INDEX",
                "currency": "USD",
            },
        ]


def _safe_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "t", "1", "yes", "y"}:
            return True
        if lowered in {"false", "f", "0", "no", "n"}:
            return False
    return None


def _normalize_asset_type(value: object) -> str | None:
    text = _safe_text(value)
    if text is None:
        return None
    mapping = {
        "cs": "equity",
        "common stock": "equity",
        "stock": "equity",
        "etf": "etf",
        "index": "index",
    }
    return mapping.get(text.lower(), text.lower())


def _normalize_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return None


def _sanitize_error_message(message: str) -> str:
    sanitized = message
    for needle in ("POLYGON_API_KEY", "apiKey", "api key", "api-key"):
        sanitized = sanitized.replace(needle, "polygon api key")
    return sanitized
