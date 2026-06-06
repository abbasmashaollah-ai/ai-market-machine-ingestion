from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.features.sector_rotation.sector_rotation_reader import (
    build_price_history_by_symbol,
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


def _full_fixture_rows(history_length: int = 90) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for offset, symbol in enumerate(get_required_symbols(), start=1):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for day in range(history_length):
            rows.append(_row(symbol, 1, 100.0 + offset + day / 100.0, date=base + timedelta(days=day)))
    return rows


class FakeCertifiedRowsClient:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.calls: list[dict[str, object]] = []

    def get_symbol_ohlcv_history(self, symbol, start_date=None, end_date=None, limit=None, order="asc"):
        self.calls.append(
            {
                "symbol": str(symbol).upper(),
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
                "order": order,
            }
        )
        normalized_symbol = str(symbol).upper()
        filtered = [row for row in self.rows if str(row.get("symbol", "")).upper() == normalized_symbol]
        return {"historical_ohlcv": filtered, "warnings": []}


def test_public_reader_functions_exist() -> None:
    assert callable(build_price_history_by_symbol)
    assert callable(fetch_sector_rotation_price_history)
    assert callable(run_sector_rotation_certified_ohlcv_dry_run)


def test_reader_builds_history_from_local_certified_rows_without_external_calls() -> None:
    rows = _fixture_rows()
    client = FakeCertifiedRowsClient(rows)

    adapter_result = fetch_sector_rotation_price_history(
        client,
        start_date="2026-01-01",
        end_date="2026-01-31",
        lookback_days=90,
    )

    assert adapter_result.no_db_writes is True
    assert adapter_result.no_vendor_calls is True
    assert adapter_result.no_scheduler_activation is True
    assert adapter_result.price_history_by_symbol["SPY"] == [100.0, 101.0]
    assert any("insufficient_history:SPY:2<90" in warning for warning in adapter_result.warnings)
    assert len(client.calls) == len(get_required_symbols(include_benchmark=True))
    assert client.calls[0]["symbol"] == "SPY"


def test_reader_dry_run_output_shape_is_stable() -> None:
    rows = _full_fixture_rows()
    client = FakeCertifiedRowsClient(rows)

    result = run_sector_rotation_certified_ohlcv_dry_run(
        client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )

    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert result.dry_run_result is not None
    assert result.dry_run_result.observation_rows
    assert result.dry_run_result.summary_row["observation_date"] == "2026-01-15"
    assert "top_sector_symbols" in result.dry_run_result.summary_row
    assert "bottom_sector_symbols" in result.dry_run_result.summary_row
    assert result.dry_run_result.writer_result.accepted_observation_count == 11
    assert result.dry_run_result.writer_result.accepted_summary_count == 1


def test_reader_warns_on_missing_required_symbol_using_local_only_input() -> None:
    rows = [row for row in _fixture_rows() if row["symbol"] != "SPY"]
    result = build_price_history_by_symbol(rows, required_symbols=("SPY", "XLK"), min_history_length=2)

    assert result.price_history_by_symbol["SPY"] == []
    assert any("missing_required_symbols:SPY" in warning for warning in result.warnings)


def test_reader_source_scan_has_no_judge_trading_risk_portfolio_or_execution_logic() -> None:
    text = Path("app/features/sector_rotation/sector_rotation_reader.py").read_text(encoding="utf-8").lower()

    assert "judge posture" not in text
    assert "trading decision" not in text
    assert "risk posture" not in text
    assert "portfolio allocation" not in text
    assert "capital logic" not in text
    assert "execution logic" not in text


def test_protected_modules_are_not_modified_by_reader_baseline_scope() -> None:
    reader_text = Path("app/features/sector_rotation/sector_rotation_reader.py").read_text(encoding="utf-8")
    protected_imports = [
        "app.features.market_risk",
        "app.features.market_regime",
        "app.features.macro_liquidity",
        "app.features.flows_positioning",
    ]

    for needle in protected_imports:
        assert needle not in reader_text


def test_baseline_is_local_and_does_not_require_live_apis_or_db() -> None:
    rows = _fixture_rows()
    client = FakeCertifiedRowsClient(rows)
    adapter_result = fetch_sector_rotation_price_history(client)

    assert adapter_result.price_history_by_symbol["XLK"]
    assert len(client.calls) == len(get_required_symbols(include_benchmark=True))
    assert "sqlalchemy" not in Path("app/features/sector_rotation/sector_rotation_reader.py").read_text(encoding="utf-8").lower()
