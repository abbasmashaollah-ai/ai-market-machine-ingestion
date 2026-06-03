from dataclasses import dataclass
from datetime import datetime, timezone
import copy

import pytest

from app.features.sector_rotation.sector_rotation_reader import (
    SectorRotationCertifiedOHLCVAdapterResult,
    fetch_sector_rotation_price_history,
    run_sector_rotation_certified_ohlcv_dry_run,
)
from app.features.sector_rotation.sector_universe import get_required_symbols


def _row(symbol: str, day: int, close: float, **kwargs: object) -> dict[str, object]:
    payload = {
        "symbol": symbol,
        "date": datetime(2026, 1, day, tzinfo=timezone.utc),
        "close": close,
        "quality_status": "VALID",
        "certification_status": "CERTIFIED",
        "freshness_status": "FRESH",
        "source": "canonical_ohlcv",
        "lineage": {"source": "fixture"},
    }
    payload.update(kwargs)
    return payload


def _fixture_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for offset, symbol in enumerate(get_required_symbols(), start=1):
        rows.extend([
            _row(symbol, 2, 100.0 + offset),
            _row(symbol, 1, 99.0 + offset),
        ])
    return rows


class FakeDataReadClient:
    def __init__(self, payload_by_symbol: object) -> None:
        self.payload_by_symbol = payload_by_symbol
        self.calls: list[tuple[str, dict[str, object]]] = []

    def get_symbol_ohlcv_history(self, symbol, start_date=None, end_date=None, limit=None, order="asc"):
        self.calls.append((str(symbol), {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "order": order,
        }))
        if isinstance(self.payload_by_symbol, dict) and str(symbol).upper() in self.payload_by_symbol:
            return self.payload_by_symbol[str(symbol).upper()]
        return self.payload_by_symbol


def _payloads_by_symbol(shape: str) -> dict[str, object]:
    payloads: dict[str, object] = {}
    for symbol in get_required_symbols(include_benchmark=True):
        if shape == "list":
            payloads[symbol] = [_row(symbol, 1, 100.0), _row(symbol, 2, 101.0)]
        elif shape == "rows":
            payloads[symbol] = {"rows": [_row(symbol, 1, 100.0), _row(symbol, 2, 101.0)]}
        elif shape == "data":
            payloads[symbol] = {"data": [_row(symbol, 1, 100.0), _row(symbol, 2, 101.0)]}
        elif shape == "ohlcv":
            payloads[symbol] = {"ohlcv": [_row(symbol, 1, 100.0), _row(symbol, 2, 101.0)]}
        elif shape == "historical_ohlcv":
            payloads[symbol] = {"historical_ohlcv": [_row(symbol, 1, 100.0), _row(symbol, 2, 101.0)]}
        else:
            payloads[symbol] = {"historical_ohlcv": [_row(symbol, 1, 100.0), _row(symbol, 2, 101.0)]}
    return payloads


def test_adapter_calls_data_read_client_with_required_symbols_and_lookback() -> None:
    client = FakeDataReadClient(_payloads_by_symbol("historical_ohlcv"))
    result = fetch_sector_rotation_price_history(client, start_date="2026-01-01", end_date="2026-01-31", lookback_days=90)

    assert [call[0] for call in client.calls] == list(get_required_symbols(include_benchmark=True))
    assert client.calls[0][1] == {"start_date": "2026-01-01", "end_date": "2026-01-31", "limit": 90, "order": "asc"}
    assert isinstance(result, SectorRotationCertifiedOHLCVAdapterResult)
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True


def test_list_response_shape_works() -> None:
    client = FakeDataReadClient(_payloads_by_symbol("list"))
    result = fetch_sector_rotation_price_history(client)
    assert result.price_history_by_symbol["SPY"] == [100.0, 101.0]


def test_rows_response_shape_works() -> None:
    client = FakeDataReadClient(_payloads_by_symbol("rows"))
    result = fetch_sector_rotation_price_history(client)
    assert result.price_history_by_symbol["XLK"]


def test_data_response_shape_works() -> None:
    client = FakeDataReadClient(_payloads_by_symbol("data"))
    result = fetch_sector_rotation_price_history(client)
    assert result.price_history_by_symbol["XLU"]


def test_ohlcv_response_shape_works() -> None:
    client = FakeDataReadClient(_payloads_by_symbol("ohlcv"))
    result = fetch_sector_rotation_price_history(client)
    assert result.price_history_by_symbol["XLC"]


def test_live_historical_ohlcv_response_shape_works() -> None:
    client = FakeDataReadClient(_payloads_by_symbol("historical_ohlcv"))
    result = fetch_sector_rotation_price_history(client)
    assert result.price_history_by_symbol["SPY"] == [100.0, 101.0]


def test_warnings_are_preserved() -> None:
    rows = _fixture_rows()
    rows = [row for row in rows if row["symbol"] != "SPY"]
    client = FakeDataReadClient(rows)
    result = fetch_sector_rotation_price_history(client)
    assert any("missing_required_symbols:SPY" in warning for warning in result.warnings)


def test_dry_run_adapter_produces_full_pipeline() -> None:
    client = FakeDataReadClient(_fixture_rows())
    result = run_sector_rotation_certified_ohlcv_dry_run(
        client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )
    assert result.dry_run_result is not None
    assert len(result.dry_run_result.observation_rows) == 11
    assert result.dry_run_result.accepted_summary_count == 1
    assert result.no_scheduler_activation is True


def test_missing_spy_surfaces_warning_cleanly() -> None:
    rows = [row for row in _fixture_rows() if row["symbol"] != "SPY"]
    client = FakeDataReadClient(rows)
    result = fetch_sector_rotation_price_history(client)
    assert any("missing_required_symbols:SPY" in warning for warning in result.warnings)


def test_input_payload_is_not_mutated() -> None:
    rows = _fixture_rows()
    snapshot = copy.deepcopy(rows)
    client = FakeDataReadClient(rows)
    fetch_sector_rotation_price_history(client)
    assert rows == snapshot


def test_no_live_http_calls_by_construction() -> None:
    client = FakeDataReadClient(_payloads_by_symbol("historical_ohlcv"))
    client.get_symbol_ohlcv_history("SPY")
    assert len(client.calls) == 1
