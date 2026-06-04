from __future__ import annotations

from app.features.market_regime.market_regime_writer import MarketRegimeMockWriter, write_market_regime_payloads


def test_market_regime_writer_accepts_valid_rows() -> None:
    writer = MarketRegimeMockWriter()
    result = write_market_regime_payloads(
        [
            {
                "observation_date": "2026-06-03",
                "source": "market_feature_bundle_summary",
                "market_regime_label": "NEUTRAL_MIXED",
                "price_states_by_symbol": {"AAPL": "UPTREND"},
            }
        ],
        writer=writer,
    )
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True

