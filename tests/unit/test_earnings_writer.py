from __future__ import annotations

from app.features.earnings.earnings_builder import build_earnings_observation
from app.features.earnings.earnings_writer import EarningsMockWriter, write_earnings_payloads
from tests.fixtures.earnings_data import build_earnings_fixture_payloads


def test_writer_accepts_valid_rows() -> None:
    payload = build_earnings_fixture_payloads()["AAPL"]
    row = build_earnings_observation("AAPL", payload, "2026-07-20")
    writer = EarningsMockWriter()
    result = write_earnings_payloads([row], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert writer.rows

