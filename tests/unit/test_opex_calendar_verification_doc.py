from __future__ import annotations

from pathlib import Path


def test_opex_calendar_verification_doc_exists_and_documents_verified_results() -> None:
    text = Path("docs/opex_calendar_verification.md").read_text(encoding="utf-8").lower()
    assert "2026 full-year generation produced 12 events" in text
    assert "june 2026 produced 1 event" in text
    assert "2026-06-19" in text
    assert "valid_count=12/12" in text
    assert "no_vendor_calls=true" in text
    assert "no_db_writes=true" in text
    assert "opex-yyyy-mm-dd" in text
    assert "america/new_york" in text
    assert "manual_rule" in text


def test_opex_calendar_verification_doc_boundary() -> None:
    text = Path("docs/opex_calendar_verification.md").read_text(encoding="utf-8").lower()
    assert "does not enable persistence" in text
    assert "ai/trading/risk/signal/regime/portfolio logic" in text
