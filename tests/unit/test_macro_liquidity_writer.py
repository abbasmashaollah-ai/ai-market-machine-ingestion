from __future__ import annotations

from app.features.macro_liquidity.macro_liquidity_writer import MacroLiquidityMockWriter, write_macro_liquidity_payloads


def test_writer_accepts_valid_rows() -> None:
    row = {
        "observation_date": "2026-06-03",
        "source": "market_feature_bundle_summary",
        "macro_liquidity_label": "MIXED_MACRO_LIQUIDITY",
    }
    writer = MacroLiquidityMockWriter()
    result = write_macro_liquidity_payloads([row], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert writer.rows

