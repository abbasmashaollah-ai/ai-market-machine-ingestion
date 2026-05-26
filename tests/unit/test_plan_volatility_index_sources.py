from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


def test_source_plan_shape():
    from app.sources.volatility_index_sources import build_volatility_index_source_candidates

    plans = build_volatility_index_source_candidates()
    assert [plan.source_name for plan in plans] == ["Polygon", "Cboe", "manual fixture"]
    assert plans[-1].status == "test_only"
    assert plans[-1].priority == 99


def test_source_plan_includes_required_candidates():
    from app.sources.volatility_index_sources import build_volatility_index_source_candidates

    names = [plan.source_name for plan in build_volatility_index_source_candidates()]
    assert "Polygon" in names
    assert "Cboe" in names
    assert "manual fixture" in names


def test_manual_fixture_marked_test_only():
    from app.sources.volatility_index_sources import build_volatility_index_source_candidates

    manual = [plan for plan in build_volatility_index_source_candidates() if plan.source_name == "manual fixture"][0]
    assert manual.status == "test_only"


def test_command_output():
    import scripts.plan_volatility_index_sources as cmd

    with patch("builtins.print") as print_mock:
        cmd.main()

    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "no_vendor_calls=True" in printed
    assert "no_db_writes=True" in printed
    assert "selected_preferred_source=Polygon" in printed
    assert "priority_order" in printed
    assert "supported_starter_symbols" in printed
    assert "next_required_step" in printed


def test_no_vendor_calls_or_db_writes():
    import scripts.plan_volatility_index_sources as cmd

    with patch("builtins.print"):
        cmd.main()


def test_no_forbidden_imports():
    text = Path("scripts/plan_volatility_index_sources.py").read_text(encoding="utf-8")
    assert "FastAPI" not in text
    assert "APIRouter" not in text
    assert "requests" not in text.lower()
    assert "httpx" not in text.lower()
    assert "alembic" not in text.lower()
    assert "ai_market_machine_data" not in text


def test_docs_cover_source_plan():
    text = Path("docs/volatility_index_source_plan.md").read_text(encoding="utf-8").lower()
    assert "volatility index source plan" in text
    assert "polygon" in text
    assert "cboe" in text
    assert "manual fixture" in text
