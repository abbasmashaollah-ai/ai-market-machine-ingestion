from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


def _module():
    import scripts.dry_run_opex_calendar as mod

    return mod


def test_third_friday_calculation() -> None:
    from app.normalization.opex_calendar import _third_friday

    assert str(_third_friday(2026, 6)) == "2026-06-19"
    assert str(_third_friday(2026, 2)) == "2026-02-20"


def test_full_year_generation() -> None:
    from app.normalization.opex_calendar import build_opex_normalized_records

    records = build_opex_normalized_records(2026)
    assert len(records) == 12
    assert records[0].event_type == "OPEX"
    assert records[0].source == "manual_rule"
    assert records[0].timezone == "America/New_York"
    assert records[0].importance == "high"
    assert records[0].event_id == "OPEX-2026-01-16"


def test_single_month_generation() -> None:
    from app.normalization.opex_calendar import build_opex_normalized_records

    records = build_opex_normalized_records(2026, 6)
    assert len(records) == 1
    assert str(records[0].event_date) == "2026-06-19"
    assert records[0].event_id == "OPEX-2026-06-19"


def test_normalized_event_shape_alignment() -> None:
    from app.normalization.event_calendar import NormalizedEventCalendarRecord

    assert tuple(NormalizedEventCalendarRecord.__dataclass_fields__.keys()) == (
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


def test_dry_run_output_and_gating() -> None:
    mod = _module()
    with patch("builtins.print") as print_mock:
        mod.main(["--year", "2026", "--month", "6"])
    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "event_count=1" in printed
    assert "normalized_count=1" in printed
    assert "valid_count=1" in printed
    assert "invalid_count=0" in printed
    assert "year=2026" in printed
    assert "month=6" in printed
    assert "no_vendor_calls=True" in printed
    assert "no_db_writes=True" in printed


def test_no_vendor_calls_no_db_writes_and_forbidden_imports() -> None:
    mod = _module()
    with patch("builtins.print") as print_mock:
        mod.main(["--year", "2026"])
    assert print_mock.mock_calls
    text = Path("scripts/dry_run_opex_calendar.py").read_text(encoding="utf-8").lower()
    for needle in ["requests", "httpx", "fastapi", "alembic", "database_url"]:
        assert needle not in text


def test_docs_coverage() -> None:
    text = Path("docs/opex_calendar_foundation.md").read_text(encoding="utf-8").lower()
    for needle in [
        "opex calendar foundation",
        "third friday",
        "manual_rule",
        "america/new_york",
        "event_id",
        "event_count",
        "no vendor calls",
        "no db writes",
        "persistence remains deferred",
    ]:
        assert needle in text

