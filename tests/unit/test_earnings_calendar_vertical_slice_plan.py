from __future__ import annotations

from pathlib import Path


def test_earnings_calendar_vertical_slice_plan_exists_and_mentions_required_terms() -> None:
    text = Path("docs/earnings_calendar_vertical_slice_plan.md").read_text(encoding="utf-8").lower()
    for needle in [
        "earnings calendar vertical slice plan",
        "event_type=earnings_date",
        "symbol_master",
        "fmp",
        "finnhub",
        "nasdaq",
        "manual_fixture",
        "event_id",
        "event_type",
        "event_date",
        "event_time",
        "timezone",
        "source",
        "symbol",
        "title",
        "importance",
        "notes",
        "time handling",
        "source and lineage expectations",
        "quality expectations",
        "preflight / runner / evidence pattern",
    ]:
        assert needle in text


def test_earnings_calendar_vertical_slice_plan_boundary_language() -> None:
    text = Path("docs/earnings_calendar_vertical_slice_plan.md").read_text(encoding="utf-8").lower()
    assert "no persistence is allowed until the data-side table and writer boundary are approved" in text
    assert "no vendor calls" in text
    assert "db reads" in text
    assert "db writes" in text
    assert "scheduler behavior" in text
    assert "fastapi routes" in text
    assert "migrations" in text
    assert "schema ownership" in text
    assert "ai, trading, risk, signal, regime, or portfolio logic" in text
