from __future__ import annotations

from pathlib import Path


def test_manual_ingestion_command_inventory_mentions_earnings_calendar_source_plan() -> None:
    text = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
    assert "scripts.plan_earnings_calendar_sources" in text
    assert "earnings calendar source plan" in text
    assert "no vendor calls" in text
    assert "no db reads" in text
    assert "no database writes" in text


def test_verify_manual_ingestion_commands_mentions_earnings_calendar_source_module() -> None:
    text = Path("scripts/verify_manual_ingestion_commands.py").read_text(encoding="utf-8").lower()
    assert "scripts.plan_earnings_calendar_sources" in text

