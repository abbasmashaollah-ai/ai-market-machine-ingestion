from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


def test_source_plan_shape() -> None:
    from app.sources.macro_event_calendar_sources import build_macro_event_calendar_source_candidates

    plans = build_macro_event_calendar_source_candidates()
    assert [plan.source_name for plan in plans] == [
        "BLS CPI",
        "Federal Reserve FOMC",
        "BLS NFP",
        "manual_fixture",
    ]
    assert plans[-1].status == "test_only"
    assert plans[-1].priority == 99


def test_source_plan_includes_required_candidates() -> None:
    from app.sources.macro_event_calendar_sources import build_macro_event_calendar_source_candidates

    names = [plan.source_name for plan in build_macro_event_calendar_source_candidates()]
    assert "BLS CPI" in names
    assert "Federal Reserve FOMC" in names
    assert "BLS NFP" in names
    assert "manual_fixture" in names


def test_manual_fixture_marked_test_only() -> None:
    from app.sources.macro_event_calendar_sources import build_macro_event_calendar_source_candidates

    manual = [plan for plan in build_macro_event_calendar_source_candidates() if plan.source_name == "manual_fixture"][0]
    assert manual.status == "test_only"


def test_command_output() -> None:
    import scripts.plan_macro_event_calendar_sources as cmd

    with patch("builtins.print") as print_mock:
        cmd.main()

    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "no_vendor_calls=True" in printed
    assert "no_db_writes=True" in printed
    assert "priority_order" in printed
    assert "supported_event_types" in printed
    assert "selected_preferred_source_by_event_type" in printed
    assert "next_required_step" in printed
    assert "event_time_handling_note" in printed


def test_no_vendor_calls_or_db_writes() -> None:
    import scripts.plan_macro_event_calendar_sources as cmd

    with patch("builtins.print"):
        cmd.main()


def test_no_forbidden_imports() -> None:
    text = Path("scripts/plan_macro_event_calendar_sources.py").read_text(encoding="utf-8")
    assert "FastAPI" not in text
    assert "APIRouter" not in text
    assert "requests" not in text.lower()
    assert "httpx" not in text.lower()
    assert "alembic" not in text.lower()
    assert "ai_market_machine_data" not in text


def test_docs_cover_source_plan() -> None:
    text = Path("docs/macro_event_calendar_source_plan.md").read_text(encoding="utf-8").lower()
    assert "macro event calendar source plan" in text
    assert "bls cpi" in text
    assert "federal reserve fomc" in text
    assert "bls nfp" in text
    assert "manual_fixture" in text
    assert "no live vendor calls" in text
    assert "no db writes" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text
