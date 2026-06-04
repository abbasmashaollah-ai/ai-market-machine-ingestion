from __future__ import annotations

from app.features.earnings.earnings_builder import build_earnings_observation
from app.features.earnings.earnings_report import build_earnings_report
from tests.fixtures.earnings_data import build_earnings_fixture_payloads


def test_report_includes_metadata_and_safety_flags() -> None:
    payload = build_earnings_fixture_payloads()["AAPL"]
    row = build_earnings_observation("AAPL", payload, "2026-07-20")
    report = build_earnings_report(row)
    assert report["symbol"] == "AAPL"
    assert report["earnings_regime_label"] == row["earnings_regime_label"]
    assert report["source_attribution"] == row["source_attribution"]
    assert report["dataset_version"] == row["dataset_version"]
    assert report["created_at"] == row["created_at"]
    assert report["updated_at"] == row["updated_at"]
    assert report["no_db_writes"] is True
    assert report["no_vendor_calls"] is True
    assert report["no_scheduler_activation"] is True

