from __future__ import annotations

from pathlib import Path


def test_readiness_summary_exists_and_mentions_required_items():
    text = Path("docs/cross_asset_ohlcv_readiness_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "vertical-slice plan exists",
        "source plan exists",
        "fixture-backed dry-run foundation exists",
        "preflight exists",
        "evidence plan exists",
        "manual inventory includes cross-asset ohlcv commands",
        "bonds/rates proxies",
        "dxy / dollar index proxy",
        "commodities",
        "crypto",
        "fx",
        "symbol_master",
        "asset-master",
        "polygon",
        "fmp",
        "manual_fixture",
        "future specialty fx/crypto path",
        "live vendor adapters are not built yet",
        "data-side asset scope is not yet approved",
        "persistence is deferred",
        "no db reads or db writes are enabled",
        "data-side asset-scope contract",
        "polygon cross-asset live dry-run planning",
        "specialty fx/crypto source research",
    ]:
        assert needle in text


def test_future_build_order_pauses_cross_asset_and_moves_breadth_next():
    text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
    assert "cross-asset ohlcv" in text
    assert "paused at readiness checkpoint" in text
    assert "persistence deferred until the approved data-side asset-scope contract exists" in text
    assert "breadth/participation" in text


def test_boundary_language_present():
    text = Path("docs/cross_asset_ohlcv_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "producer-planning side only" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text
