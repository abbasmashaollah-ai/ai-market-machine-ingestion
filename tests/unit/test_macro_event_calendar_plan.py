from __future__ import annotations

from pathlib import Path


def test_macro_event_calendar_plan_exists_and_mentions_required_terms() -> None:
    text = Path("docs/macro_event_calendar_plan.md").read_text(encoding="utf-8").lower()
    for needle in [
        "macro event calendar plan",
        "cpi",
        "fomc",
        "nfp",
        "bls",
        "federal reserve",
        "manual fixture",
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
        "timezone and time handling",
        "source and lineage expectations",
    ]:
        assert needle in text


def test_macro_event_calendar_plan_boundary_language() -> None:
    text = Path("docs/macro_event_calendar_plan.md").read_text(encoding="utf-8").lower()
    assert "no persistence is allowed until the data-side table and writer boundary are approved" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text

