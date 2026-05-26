from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Protocol

from app.normalization.volatility_index import (
    NormalizedVolatilityIndexRecord,
    STARTER_VOLATILITY_INDEX_SYMBOLS,
    normalize_volatility_index_record,
)
from app.vendors.common.errors import VendorRateLimitedError
from app.vendors.polygon.client import PolygonClient, PolygonClientConfig, build_polygon_client


@dataclass(frozen=True)
class PolygonVolatilityIndexSourceConfig:
    api_key: str | None = None
    base_url: str = "https://api.polygon.io"
    timeout_seconds: float = 30.0


class PolygonVolatilityIndexSource(Protocol):
    def fetch_aggregates_raw(
        self,
        ticker: str,
        from_date: str,
        to_date: str,
        *,
        adjusted: bool = True,
    ) -> list[dict[str, object]]:
        ...


def polygon_vendor_symbol(symbol: str) -> str:
    mapping = {
        "VIX": "I:VIX",
        "VVIX": "I:VVIX",
        "VXN": "I:VXN",
        "RVX": "I:RVX",
    }
    return mapping.get(symbol.upper(), symbol)


def polygon_canonical_symbol(vendor_symbol: str) -> str:
    reverse = {
        "I:VIX": "VIX",
        "I:VVIX": "VVIX",
        "I:VXN": "VXN",
        "I:RVX": "RVX",
    }
    return reverse.get(vendor_symbol.upper(), vendor_symbol)


class PolygonVolatilityIndexAdapter:
    def __init__(
        self,
        config: PolygonVolatilityIndexSourceConfig,
        client: PolygonClient | None = None,
    ) -> None:
        self.config = config
        self._client = client

    def _client_or_build(self) -> PolygonClient:
        if self._client is not None:
            return self._client
        if not self.config.api_key:
            raise RuntimeError("POLYGON_API_KEY is required for live Polygon volatility index checks")
        return build_polygon_client(
            PolygonClientConfig(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout_seconds=self.config.timeout_seconds,
            )
        )

    def build_sample_payloads(self) -> list[dict[str, object]]:
        return [
            {"symbol": "VIX", "observation_date": "2026-05-21", "value": 18.2, "source": "polygon", "vendor_symbol": "I:VIX", "unit": "index", "notes": "fixture"},
            {"symbol": "VVIX", "observation_date": "2026-05-21", "value": 92.1, "source": "polygon", "vendor_symbol": "I:VVIX", "unit": "index", "notes": "fixture"},
            {"symbol": "VXN", "observation_date": "2026-05-21", "value": 21.7, "source": "polygon", "vendor_symbol": "I:VXN", "unit": "index", "notes": "fixture"},
            {"symbol": "RVX", "observation_date": "2026-05-21", "value": 25.4, "source": "polygon", "vendor_symbol": "I:RVX", "unit": "index", "notes": "fixture"},
        ]

    def fetch_symbol_aggregates_raw(
        self,
        symbol: str,
        *,
        max_observations: int | None = None,
    ) -> list[dict[str, object]]:
        vendor_symbol = polygon_vendor_symbol(symbol)
        end_date = date.today().isoformat()
        start_date = "2000-01-01"
        try:
            payload = self._client_or_build().fetch_aggregates_raw(vendor_symbol, start_date, end_date, adjusted=False)
        except VendorRateLimitedError:
            raise
        except Exception as exc:
            raise RuntimeError(_sanitize_error_message(str(exc))) from exc
        if not payload:
            raise RuntimeError("polygon returned no volatility observations")
        records = _normalize_polygon_aggregate_payloads(symbol=symbol, vendor_symbol=vendor_symbol, payload=payload)
        if not records:
            raise RuntimeError("polygon returned no valid volatility observations")
        records.sort(key=lambda record: (record.observation_date or date.min, record.symbol or ""))
        if max_observations is not None:
            records = records[-max_observations:]
        return [record.__dict__ for record in records]

    def fetch_symbol_records(
        self,
        symbol: str,
        *,
        max_observations: int | None = None,
    ) -> list[NormalizedVolatilityIndexRecord]:
        raw_records = self.fetch_symbol_aggregates_raw(symbol, max_observations=max_observations)
        return [normalize_volatility_index_record(record) for record in raw_records]


def _normalize_polygon_aggregate_payloads(
    *,
    symbol: str,
    vendor_symbol: str,
    payload: list[dict[str, object]],
) -> list[NormalizedVolatilityIndexRecord]:
    records: list[NormalizedVolatilityIndexRecord] = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        timestamp = row.get("t")
        observation_date = None
        if isinstance(timestamp, (int, float)):
            observation_date = datetime.fromtimestamp(float(timestamp) / 1000.0, tz=timezone.utc).date()
        value = row.get("c")
        vendor_value = row.get("ticker") or row.get("symbol") or vendor_symbol
        normalized_symbol = polygon_canonical_symbol(str(vendor_value))
        normalized = normalize_volatility_index_record(
            {
                "symbol": normalized_symbol if normalized_symbol else symbol,
                "observation_date": observation_date.isoformat() if observation_date else None,
                "value": value,
                "source": "polygon",
                "vendor_symbol": vendor_symbol,
                "unit": "index",
                "notes": row.get("notes") or "polygon aggregate",
            }
        )
        records.append(normalized)
    return records


def _sanitize_error_message(message: str) -> str:
    sanitized = message
    for needle in ("POLYGON_API_KEY", "apiKey", "api key", "api-key"):
        sanitized = sanitized.replace(needle, "polygon api key")
    return sanitized


def is_entitlement_failure(message: str) -> bool:
    lowered = message.lower()
    return "401" in lowered or "unauthorized" in lowered or "entitlement" in lowered or "forbidden" in lowered
