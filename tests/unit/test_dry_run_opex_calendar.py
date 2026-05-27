from __future__ import annotations

import subprocess
import sys
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


def test_show_events_prints_normalized_records() -> None:
    mod = _module()
    with patch("builtins.print") as print_mock:
        mod.main(["--year", "2026", "--show-events"])
    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "events=(" in printed
    assert "OPEX-2026-01-16" in printed


def test_show_invalid_prints_invalid_records_when_present() -> None:
    mod = _module()
    fake_invalid = ({"record": "bad", "errors": ("event_id is required",)},)
    with patch("scripts.dry_run_opex_calendar.build_opex_validation_results", return_value=fake_invalid), patch(
        "builtins.print"
    ) as print_mock:
        mod.main(["--year", "2026", "--show-invalid"])
    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "invalid_records=(" in printed
    assert "event_id is required" in printed


def test_no_vendor_calls_no_db_writes_and_forbidden_imports() -> None:
    mod = _module()
    with patch("builtins.print") as print_mock:
        mod.main(["--year", "2026"])
    assert print_mock.mock_calls
    text = Path("scripts/dry_run_opex_calendar.py").read_text(encoding="utf-8").lower()
    for needle in ["requests", "httpx", "fastapi", "alembic", "database_url"]:
        assert needle not in text


def test_docs_and_cli_agree_on_optional_flags() -> None:
    text = Path("docs/opex_calendar_foundation.md").read_text(encoding="utf-8").lower()
    assert "--show-events" in text
    assert "--show-invalid" in text
    script_text = Path("scripts/dry_run_opex_calendar.py").read_text(encoding="utf-8").lower()
    assert "--show-events" in script_text
    assert "--show-invalid" in script_text


def test_cli_help_prints_without_requires_error() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.dry_run_opex_calendar", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--show-events" in result.stdout
    assert "--show-invalid" in result.stdout
    assert "--year YEAR" in result.stdout or "--year" in result.stdout
    assert "required" not in result.stderr.lower()


def test_cli_show_events_outputs_records() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.dry_run_opex_calendar", "--year", "2026", "--show-events"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "event_count=12" in result.stdout
    assert "events=(" in result.stdout
    assert "OPEX-2026-01-16" in result.stdout


def test_cli_month_and_show_events_outputs_single_month() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.dry_run_opex_calendar", "--year", "2026", "--month", "6", "--show-events"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "event_count=1" in result.stdout
    assert "month=6" in result.stdout
    assert "OPEX-2026-06-19" in result.stdout


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
