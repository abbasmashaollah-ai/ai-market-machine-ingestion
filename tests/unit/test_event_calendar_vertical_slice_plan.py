from __future__ import annotations

from pathlib import Path


def test_event_calendar_vertical_slice_plan_exists_and_mentions_required_terms():
    plan = Path(__file__).resolve().parents[2] / "docs" / "event_calendar_vertical_slice_plan.md"
    text = plan.read_text(encoding="utf-8").lower()

    assert plan.exists()
    for needle in [
        "purpose",
        "cpi",
        "fomc",
        "nfp",
        "opex",
        "earnings dates",
        "fred",
        "bls",
        "fed official sources",
        "nasdaq",
        "fmp",
        "finnhub",
        "manual fixture",
        "event_id",
        "event_type",
        "event_date",
        "event_time",
        "timezone",
        "source",
        "title",
        "importance",
        "lineage expectations",
        "preflight/runner/evidence pattern",
        "no ai/trading/risk/signal/regime/portfolio logic",
    ]:
        assert needle in text
