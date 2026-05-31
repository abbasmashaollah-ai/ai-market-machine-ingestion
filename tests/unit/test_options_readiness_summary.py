from __future__ import annotations

from pathlib import Path


def test_readiness_summary_exists_and_mentions_required_items():
    text = Path("docs/options_readiness_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "vertical-slice plan exists",
        "source plan exists",
        "fixture-backed dry-run foundation exists",
        "preflight exists",
        "evidence plan exists",
        "manual inventory includes options commands",
        "option chains",
        "option contracts",
        "open interest",
        "implied volatility",
        "put/call volume",
        "put/call open interest",
        "expiration metadata",
        "symbol_master",
        "polygon",
        "tradier",
        "occ-derived",
        "manual_fixture",
        "live adapters are not built yet",
        "data-side contracts are not yet approved",
        "persistence is deferred",
        "no db reads or db writes are enabled",
        "data-side options contract",
        "polygon options live dry-run planning",
        "tradier live dry-run planning",
        "occ-derived metadata planning",
    ]:
        assert needle in text


def test_future_build_order_pauses_options_and_moves_flows_next():
    text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
    assert "options" in text
    assert "paused at readiness checkpoint" in text
    assert "persistence deferred until the approved data-side contract exists" in text
    assert "flows/positioning planning" in text


def test_boundary_language_present():
    text = Path("docs/options_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "producer-planning side only" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text
