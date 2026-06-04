from __future__ import annotations

from app.features.market_risk.market_risk_writer import MarketRiskMockWriter, write_market_risk_payloads


def test_writer_accepts_valid_rows() -> None:
    row = {
        "observation_date": "2026-06-03",
        "source": "market_feature_bundle_summary",
        "market_risk_label": "MIXED_MARKET_RISK",
        "price_states_by_symbol": {},
    }
    writer = MarketRiskMockWriter()
    result = write_market_risk_payloads([row], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert writer.rows

