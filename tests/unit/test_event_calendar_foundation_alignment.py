from __future__ import annotations

from pathlib import Path

from app.normalization.event_calendar import NormalizedEventCalendarRecord


def test_event_calendar_normalized_record_fields_align_with_data_contract() -> None:
    fields = tuple(NormalizedEventCalendarRecord.__dataclass_fields__.keys())
    assert fields == (
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
    )


def test_event_calendar_foundation_doc_mentions_contract_alignment_and_writer_plan() -> None:
    text = Path("docs/event_calendar_foundation.md").read_text(encoding="utf-8").lower()
    assert "aligned to the canonical event calendar contract" in text
    assert "writer plan is documentation only" in text


def test_event_calendar_evidence_plan_mentions_writer_deferment() -> None:
    text = Path("docs/event_calendar_evidence_plan.md").read_text(encoding="utf-8").lower()
    assert "writer-readiness planning remains documentation only" in text
    assert "writer plan is deferred and does not enable persistence" in text

