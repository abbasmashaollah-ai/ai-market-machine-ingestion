from __future__ import annotations

from pathlib import Path


def test_readiness_summary_exists_and_mentions_required_items():
    text = Path("docs/breadth_participation_readiness_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "vertical-slice plan exists",
        "source plan exists",
        "fixture-backed dry-run foundation exists",
        "preflight exists",
        "evidence plan exists",
        "manual inventory includes breadth/participation commands",
        "advance_decline_count",
        "new_highs_new_lows",
        "percent_above_moving_average",
        "up_down_volume",
        "sector_participation",
        "index_universe_breadth",
        "symbol_master",
        "etf/index universe",
        "vendor breadth feeds",
        "exchange breadth feeds",
        "derived-from-ohlcv",
        "manual_fixture",
        "live vendor adapters are not built yet",
        "data-side contracts are not yet approved",
        "persistence is deferred",
        "no db reads or db writes are enabled",
        "data-side breadth contract",
        "derived-from-ohlcv planning",
        "vendor/exchange breadth source research",
    ]:
        assert needle in text


def test_future_build_order_pauses_breadth_and_moves_options_next():
    text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
    assert "breadth/participation" in text
    assert "paused at readiness checkpoint" in text
    assert "persistence deferred until the approved data-side contract exists" in text
    assert "options planning" in text


def test_boundary_language_present():
    text = Path("docs/breadth_participation_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "producer-planning side only" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text
