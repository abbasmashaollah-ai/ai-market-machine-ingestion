from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


def test_source_plan_shape():
    from app.sources.fundamentals_filings_sources import build_fundamentals_filings_source_candidates

    plans = build_fundamentals_filings_source_candidates()
    assert [plan.source_name for plan in plans] == ["SEC", "FMP", "Finnhub", "manual_fixture"]
    assert plans[-1].status == "test_only"
    assert plans[-1].priority == 99


def test_source_plan_includes_required_candidates():
    from app.sources.fundamentals_filings_sources import build_fundamentals_filings_source_candidates

    names = [plan.source_name for plan in build_fundamentals_filings_source_candidates()]
    assert "SEC" in names
    assert "FMP" in names
    assert "Finnhub" in names
    assert "manual_fixture" in names


def test_manual_fixture_marked_test_only():
    from app.sources.fundamentals_filings_sources import build_fundamentals_filings_source_candidates

    manual = [plan for plan in build_fundamentals_filings_source_candidates() if plan.source_name == "manual_fixture"][0]
    assert manual.status == "test_only"


def test_command_output():
    import scripts.plan_fundamentals_filings_sources as cmd

    with patch("builtins.print") as print_mock:
        cmd.main()

    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "no_vendor_calls=True" in printed
    assert "no_db_reads=True" in printed
    assert "no_db_writes=True" in printed
    assert "priority_order" in printed
    assert "supported_record_families" in printed
    assert "next_required_step" in printed


def test_no_forbidden_imports():
    text = Path("scripts/plan_fundamentals_filings_sources.py").read_text(encoding="utf-8")
    assert "FastAPI" not in text
    assert "APIRouter" not in text
    assert "requests" not in text.lower()
    assert "httpx" not in text.lower()
    assert "alembic" not in text.lower()
    assert "ai_market_machine_data" not in text


def test_docs_cover_source_plan():
    text = Path("docs/fundamentals_filings_source_plan.md").read_text(encoding="utf-8").lower()
    assert "fundamentals/filings source plan" in text
    assert "sec" in text
    assert "fmp" in text
    assert "finnhub" in text
    assert "manual_fixture" in text


def test_manual_inventory_wiring_if_command_is_added():
    text = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
    assert "scripts.plan_fundamentals_filings_sources" in text
