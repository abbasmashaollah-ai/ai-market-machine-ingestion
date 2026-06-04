import copy
from datetime import datetime, timezone

import pytest

from app.features.sector_rotation.sector_rotation_job import run_sector_rotation_dry_run
from app.features.sector_rotation.sector_universe import get_sector_symbols


def _sample_price_history() -> dict[str, list[float]]:
    history = list(range(100, 165))
    return {
        "SPY": history,
        "XLK": [50 + i * 0.5 for i in range(65)],
        "XLY": [60 + i * 0.4 for i in range(65)],
        "XLP": [40 + i * 0.1 for i in range(65)],
        "XLE": [30 + i * 0.3 for i in range(65)],
        "XLF": [35 + i * 0.2 for i in range(65)],
        "XLV": [45 + i * 0.15 for i in range(65)],
        "XLI": [25 + i * 0.25 for i in range(65)],
        "XLB": [20 + i * 0.12 for i in range(65)],
        "XLRE": [55 + i * 0.05 for i in range(65)],
        "XLC": [48 + i * 0.22 for i in range(65)],
        "XLU": [42 + i * 0.08 for i in range(65)],
    }


def test_complete_sample_data_produces_full_pipeline() -> None:
    price_history = _sample_price_history()
    result = run_sector_rotation_dry_run(price_history, observation_date="2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))

    assert len(result.observation_rows) == 11
    assert result.accepted_observation_count == 11
    assert result.accepted_summary_count == 1
    assert result.writer_result.accepted_observation_count == 11
    assert result.writer_result.accepted_summary_count == 1
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert result.summary_row["descriptive_rotation_state"] is not None
    assert "cyclical_leadership_score" in result.summary_row


def test_missing_spy_raises_clear_error() -> None:
    price_history = _sample_price_history()
    price_history.pop("SPY")
    with pytest.raises(ValueError, match="SPY benchmark is required"):
        run_sector_rotation_dry_run(price_history, observation_date="2026-01-15")


def test_no_sector_symbols_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="at least one sector symbol is required"):
        run_sector_rotation_dry_run({"SPY": [1, 2, 3]}, observation_date="2026-01-15")


def test_insufficient_60d_history_does_not_fail() -> None:
    price_history = _sample_price_history()
    price_history["XLK"] = price_history["XLK"][-10:]
    result = run_sector_rotation_dry_run(price_history, observation_date="2026-01-15")
    assert result.no_db_writes is True
    assert any("insufficient_history_for_60d_outputs" in warning for warning in result.warnings)


def test_input_price_histories_are_not_mutated() -> None:
    price_history = _sample_price_history()
    snapshot = copy.deepcopy(price_history)
    run_sector_rotation_dry_run(price_history, observation_date="2026-01-15")
    assert price_history == snapshot


def test_sector_universe_order_is_preserved() -> None:
    result = run_sector_rotation_dry_run(_sample_price_history(), observation_date="2026-01-15")
    assert [row["sector_symbol"] for row in result.observation_rows] == list(get_sector_symbols())
