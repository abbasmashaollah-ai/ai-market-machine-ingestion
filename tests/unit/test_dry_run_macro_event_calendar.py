from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch


def _module():
    import scripts.dry_run_macro_event_calendar as mod

    return mod


def test_fixture_generation() -> None:
    from app.normalization.macro_event_calendar import build_macro_event_calendar_records

    records = build_macro_event_calendar_records()
    assert [record.event_type for record in records] == ["CPI", "FOMC", "NFP"]
    assert records[0].event_id == "CPI-2026-06-11"
    assert records[1].event_id == "FOMC-2026-06-17"
    assert records[2].event_id == "NFP-2026-06-05"


def test_event_type_filtering() -> None:
    from app.normalization.macro_event_calendar import build_macro_event_calendar_records

    records = build_macro_event_calendar_records(("CPI", "NFP"))
    assert [record.event_type for record in records] == ["CPI", "NFP"]


def test_normalized_field_alignment() -> None:
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


def test_dry_run_output() -> None:
    mod = _module()
    with patch("builtins.print") as print_mock:
        mod.main([])
    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "event_count=3" in printed
    assert "normalized_count=3" in printed
    assert "valid_count=3" in printed
    assert "invalid_count=0" in printed
    assert "event_types=['CPI', 'FOMC', 'NFP']" in printed
    assert "no_vendor_calls=True" in printed
    assert "no_db_writes=True" in printed


def test_show_events_and_show_invalid() -> None:
    mod = _module()
    with patch("builtins.print") as print_mock:
        mod.main(["--show-events", "--show-invalid"])
    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "events=(" in printed
    assert "invalid_records=(" in printed


def test_cli_invocations() -> None:
    help_result = subprocess.run(
        [sys.executable, "-m", "scripts.dry_run_macro_event_calendar", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_result.returncode == 0
    assert "--event-type" in help_result.stdout
    assert "--show-events" in help_result.stdout
    assert "--show-invalid" in help_result.stdout

    filtered_result = subprocess.run(
        [sys.executable, "-m", "scripts.dry_run_macro_event_calendar", "--event-type", "CPI", "--event-type", "NFP"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert filtered_result.returncode == 0
    assert "event_types=['CPI', 'NFP']" in filtered_result.stdout


def test_no_vendor_calls_no_db_writes_and_forbidden_imports() -> None:
    mod = _module()
    with patch("builtins.print") as print_mock:
        mod.main([])
    assert print_mock.mock_calls
    text = Path("scripts/dry_run_macro_event_calendar.py").read_text(encoding="utf-8").lower()
    for needle in ["requests", "httpx", "fastapi", "alembic", "database_url"]:
        assert needle not in text


def test_docs_coverage() -> None:
    text = Path("docs/macro_event_calendar_foundation.md").read_text(encoding="utf-8").lower()
    for needle in [
        "macro event calendar foundation",
        "cpi",
        "fomc",
        "nfp",
        "manual_fixture",
        "america/new_york",
        "event_count",
        "no vendor calls",
        "no db writes",
        "no ai/trading/risk/signal/regime/portfolio logic",
    ]:
        assert needle in text

