from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch


def _module():
    import scripts.dry_run_earnings_calendar as mod

    return mod


def test_fixture_generation() -> None:
    from app.normalization.earnings_calendar import build_earnings_calendar_records

    records = build_earnings_calendar_records()
    assert [record.symbol for record in records] == ["AAPL", "MSFT", "NVDA"]
    assert records[0].event_id == "EARNINGS-AAPL-2026-07-30"
    assert records[1].event_time is None


def test_symbol_filtering() -> None:
    from app.normalization.earnings_calendar import build_earnings_calendar_records

    records = build_earnings_calendar_records(("MSFT",))
    assert [record.symbol for record in records] == ["MSFT"]


def test_nullable_event_time_and_timezone_behavior() -> None:
    from app.normalization.earnings_calendar import build_earnings_calendar_records

    records = build_earnings_calendar_records(("MSFT", "AAPL"))
    msft = [record for record in records if record.symbol == "MSFT"][0]
    aapl = [record for record in records if record.symbol == "AAPL"][0]
    assert msft.event_time is None
    assert aapl.event_time is not None
    assert str(aapl.event_time) == "16:05:00"
    assert aapl.timezone == "America/New_York"


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
    assert "symbols=['AAPL', 'MSFT', 'NVDA']" in printed
    assert "no_vendor_calls=True" in printed
    assert "no_db_reads=True" in printed
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
        [sys.executable, "-m", "scripts.dry_run_earnings_calendar", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_result.returncode == 0
    assert "--symbol" in help_result.stdout
    assert "--show-events" in help_result.stdout
    assert "--show-invalid" in help_result.stdout

    filtered_result = subprocess.run(
        [sys.executable, "-m", "scripts.dry_run_earnings_calendar", "--symbol", "MSFT"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert filtered_result.returncode == 0
    assert "symbols=['MSFT']" in filtered_result.stdout


def test_no_vendor_calls_no_db_reads_no_db_writes_and_forbidden_imports() -> None:
    mod = _module()
    with patch("builtins.print") as print_mock:
        mod.main([])
    assert print_mock.mock_calls
    text = Path("scripts/dry_run_earnings_calendar.py").read_text(encoding="utf-8").lower()
    for needle in ["requests", "httpx", "fastapi", "alembic", "database_url"]:
        assert needle not in text


def test_docs_coverage() -> None:
    text = Path("docs/earnings_calendar_foundation.md").read_text(encoding="utf-8").lower()
    for needle in [
        "earnings calendar foundation",
        "earnings_date",
        "manual_fixture",
        "event_time` nullable",
        "timezone` explicit when `event_time` exists",
        "event_count",
        "no vendor calls",
        "no db reads",
        "no db writes",
    ]:
        assert needle in text
