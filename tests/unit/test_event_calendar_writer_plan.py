from __future__ import annotations

from pathlib import Path


def test_event_calendar_writer_plan_exists_and_documents_required_terms() -> None:
    path = Path("docs/event_calendar_writer_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "event calendar writer plan",
        "future writer responsibilities",
        "event_id",
        "event_type + event_date + source + symbol",
        "confirmed-write gating",
        "batch commit and rollback expectations",
        "run, quality, and lineage",
        "does not own schema design",
        "migrations",
        "read-only",
        "does not enable database writes",
        "persistence remains deferred",
    ]:
        assert needle in text


def test_event_calendar_writer_plan_keeps_persistence_deferred() -> None:
    text = Path("docs/event_calendar_writer_plan.md").read_text(encoding="utf-8").lower()
    assert "does not enable database writes" in text
    assert "confirmed-write decision" in text
    assert "quality checks pass for the batch" in text


def test_event_calendar_writer_plan_has_no_forbidden_logic() -> None:
    text = Path("docs/event_calendar_writer_plan.md").read_text(encoding="utf-8").lower()
    for needle in [
        "ai/trading/risk/signal/regime/portfolio logic",
        "scheduler",
        "fastapi",
    ]:
        assert needle not in text

