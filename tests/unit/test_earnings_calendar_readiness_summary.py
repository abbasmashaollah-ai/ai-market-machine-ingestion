from __future__ import annotations

from pathlib import Path


def test_earnings_calendar_readiness_summary_exists_and_mentions_required_items() -> None:
    text = Path("docs/earnings_calendar_readiness_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "earnings calendar readiness summary",
        "earnings vertical-slice plan exists",
        "fixture-backed dry-run foundation exists",
        "source plan exists",
        "manual inventory includes earnings commands",
        "event_type=earnings_date",
        "symbol_master",
        "fmp",
        "finnhub",
        "nasdaq",
        "manual_fixture",
        "live vendor adapters are not built yet",
        "persistence remains deferred",
        "no db reads or db writes are enabled",
    ]:
        assert needle in text


def test_earnings_calendar_readiness_summary_boundary_language() -> None:
    text = Path("docs/earnings_calendar_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "no vendor calls are made by this summary" in text
    assert "no scheduler, fastapi route, migration, schema ownership, ai, trading, risk, signal, regime, or portfolio logic belongs here" in text


def test_event_calendar_readiness_summary_references_earnings_and_pause() -> None:
    text = Path("docs/event_calendar_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "earnings calendar readiness summary exists" in text
    assert "paused cleanly before live vendor adapters" in text

