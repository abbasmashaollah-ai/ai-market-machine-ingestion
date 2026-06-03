from datetime import datetime, timezone
import copy

import pytest

from app.features.sector_rotation.sector_rotation_job import run_sector_rotation_dry_run
from app.features.sector_rotation.sector_rotation_reader import (
    CertifiedOHLCVRow,
    build_price_history_by_symbol,
    coerce_certified_ohlcv_row,
    get_missing_required_symbols,
    validate_reader_history_coverage,
)
from app.features.sector_rotation.sector_universe import get_required_symbols


def _row(symbol: str, day: int, close: float, **kwargs: object) -> dict[str, object]:
    base = {
        "symbol": symbol,
        "date": datetime(2026, 1, day, tzinfo=timezone.utc),
        "close": close,
        "quality_status": "VALID",
        "certification_status": "CERTIFIED",
        "freshness_status": "FRESH",
        "source": "canonical_ohlcv",
        "lineage": {"source": "fixture"},
    }
    base.update(kwargs)
    return base


def _fixture_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for offset, symbol in enumerate(get_required_symbols(), start=1):
        if symbol == "SPY":
            rows.extend([
                _row(symbol, 2, 101.0),
                _row(symbol, 1, 100.0),
            ])
        else:
            rows.extend([
                _row(symbol, 2, 50.0 + offset),
                _row(symbol, 1, 49.0 + offset),
            ])
    return rows


def test_dictionary_rows_are_accepted_and_sorted() -> None:
    rows = [_row("xlk", 2, 2.0), _row("XLK", 1, 1.0)]
    result = build_price_history_by_symbol(rows, required_symbols=("SPY", "XLK"))

    assert result.price_history_by_symbol == {"SPY": [], "XLK": [1.0, 2.0]}
    assert any("missing_required_symbols:SPY" in warning for warning in result.warnings)


def test_dataclass_rows_are_accepted() -> None:
    rows = [
        CertifiedOHLCVRow(symbol="spy", date=datetime(2026, 1, 2, tzinfo=timezone.utc), close=101.0),
        CertifiedOHLCVRow(symbol="spy", date=datetime(2026, 1, 1, tzinfo=timezone.utc), close=100.0),
    ]
    result = build_price_history_by_symbol(rows, required_symbols=("SPY",))
    assert result.price_history_by_symbol == {"SPY": [100.0, 101.0]}


def test_coerce_certified_ohlcv_row_normalizes_symbol() -> None:
    row = coerce_certified_ohlcv_row({"symbol": "xlk", "timestamp": "2026-01-01", "close": 1.0})
    assert row["symbol"] == "XLK"


def test_missing_close_row_is_ignored_with_warning() -> None:
    rows = [_row("XLK", 1, 1.0), {"symbol": "XLK", "date": datetime(2026, 1, 2, tzinfo=timezone.utc), "close": None}]
    result = build_price_history_by_symbol(rows, required_symbols=("XLK",))
    assert result.price_history_by_symbol["XLK"] == [1.0]
    assert any("missing_or_invalid_close:XLK" in warning for warning in result.warnings)


def test_quality_and_certification_rejections_warn_and_skip() -> None:
    rows = [
        _row("XLK", 1, 1.0, quality_status="FAILED"),
        _row("XLF", 1, 2.0, certification_status="REJECTED"),
    ]
    result = build_price_history_by_symbol(rows, required_symbols=("XLK", "XLF"))
    assert result.price_history_by_symbol["XLK"] == []
    assert result.price_history_by_symbol["XLF"] == []
    assert any("rejected_quality_status:XLK:FAILED" in warning for warning in result.warnings)
    assert any("rejected_certification_status:XLF:REJECTED" in warning for warning in result.warnings)


def test_missing_required_symbol_and_insufficient_history_warnings() -> None:
    rows = [_row("XLK", 1, 1.0)]
    result = build_price_history_by_symbol(rows, required_symbols=("SPY", "XLK"), min_history_length=2)
    assert any("missing_required_symbols:SPY" in warning for warning in result.warnings)
    assert any("insufficient_history:XLK:1<2" in warning for warning in result.warnings)


def test_get_missing_required_symbols_and_coverage_helpers() -> None:
    history = {"SPY": [100.0], "XLK": [1.0]}
    assert get_missing_required_symbols(history, required_symbols=("SPY", "XLK", "XLU")) == ("XLU",)
    valid, warnings = validate_reader_history_coverage(history, required_symbols=("SPY", "XLK"), min_history_length=1)
    assert valid is True
    assert warnings == ()


def test_input_rows_are_not_mutated() -> None:
    rows = [_row("XLK", 1, 1.0), _row("XLK", 2, 2.0)]
    snapshot = copy.deepcopy(rows)
    build_price_history_by_symbol(rows, required_symbols=("XLK",))
    assert rows == snapshot


def test_output_can_feed_dry_run_job() -> None:
    rows = _fixture_rows()
    reader_result = build_price_history_by_symbol(rows, required_symbols=get_required_symbols(), min_history_length=2)
    result = run_sector_rotation_dry_run(
        reader_result.price_history_by_symbol,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )
    assert len(result.observation_rows) == 11
    assert result.writer_result.accepted_observation_count == 11
    assert result.writer_result.accepted_summary_count == 1


def test_no_vendor_api_db_dependency_by_construction() -> None:
    rows = _fixture_rows()
    reader_result = build_price_history_by_symbol(rows, required_symbols=get_required_symbols(), min_history_length=2)
    assert reader_result.price_history_by_symbol["SPY"] == [100.0, 101.0]
    assert set(reader_result.price_history_by_symbol) == set(get_required_symbols())
    assert reader_result.warnings == ()
