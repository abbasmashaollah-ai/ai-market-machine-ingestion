from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


def test_source_plan_shape():
    from app.sources.breadth_participation_sources import build_breadth_participation_source_candidates

    plans = build_breadth_participation_source_candidates()
    assert [plan.source_name for plan in plans] == [
        "vendor_breadth_feed",
        "exchange_breadth_feed",
        "derived_from_ohlcv",
        "manual_fixture",
    ]
    assert plans[-1].status == "test_only"
    assert plans[-1].priority == 99


def test_source_plan_includes_required_candidates():
    from app.sources.breadth_participation_sources import build_breadth_participation_source_candidates

    names = [plan.source_name for plan in build_breadth_participation_source_candidates()]
    assert "vendor_breadth_feed" in names
    assert "exchange_breadth_feed" in names
    assert "derived_from_ohlcv" in names
    assert "manual_fixture" in names


def test_manual_fixture_marked_test_only():
    from app.sources.breadth_participation_sources import build_breadth_participation_source_candidates

    manual = [plan for plan in build_breadth_participation_source_candidates() if plan.source_name == "manual_fixture"][0]
    assert manual.status == "test_only"


def test_command_output():
    import scripts.plan_breadth_participation_sources as cmd

    with patch("builtins.print") as print_mock:
        cmd.main()

    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "no_vendor_calls=True" in printed
    assert "no_db_reads=True" in printed
    assert "no_db_writes=True" in printed
    assert "priority_order" in printed
    assert "target_metrics" in printed
    assert "next_required_step" in printed


def test_no_forbidden_imports():
    text = Path("scripts/plan_breadth_participation_sources.py").read_text(encoding="utf-8")
    assert "FastAPI" not in text
    assert "APIRouter" not in text
    assert "requests" not in text.lower()
    assert "httpx" not in text.lower()
    assert "alembic" not in text.lower()
    assert "ai_market_machine_data" not in text


def test_docs_cover_source_plan():
    text = Path("docs/breadth_participation_source_plan.md").read_text(encoding="utf-8").lower()
    assert "breadth/participation source plan" in text
    assert "vendor_breadth_feed" in text
    assert "exchange_breadth_feed" in text
    assert "derived_from_ohlcv" in text
    assert "manual_fixture" in text


def test_dependencies_documented():
    text = Path("docs/breadth_participation_vertical_slice_plan.md").read_text(encoding="utf-8").lower()
    assert "symbol_master" in text
    assert "etf/index universe" in text
    assert "persistence deferred until data-side contracts are approved" in text
