from __future__ import annotations

from pathlib import Path


def test_event_calendar_evidence_plan_exists_and_mentions_required_terms():
    plan = Path(__file__).resolve().parents[2] / "docs" / "event_calendar_evidence_plan.md"
    text = plan.read_text(encoding="utf-8").lower()

    assert plan.exists()
    for needle in [
        "evidence planning layer",
        "event row counts by event_type",
        "latest event_date by event_type",
        "missing event_type coverage",
        "timezone completeness",
        "missing title count",
        "missing source count",
        "symbol coverage for earnings_date events",
        "run/quality/lineage once persistence exists",
        "no db reads yet",
        "no db writes yet",
        "persistence contract must be approved",
    ]:
        assert needle in text


def test_event_calendar_evidence_plan_defers_persistence_and_avoids_forbidden_logic():
    plan = Path(__file__).resolve().parents[2] / "docs" / "event_calendar_evidence_plan.md"
    text = plan.read_text(encoding="utf-8").lower()

    assert "persistence" in text
    assert "approved" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" not in text
