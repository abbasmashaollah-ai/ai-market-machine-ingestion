from app.features.sector_money_flow.sector_money_flow_observation_builder import build_sector_money_flow_observation


def test_sector_money_flow_observation_builder_valid_contract():
    row = {
        "observation_date": "2026-06-15",
        "sector_symbol": "XLK",
        "source_vendor": "vendor_a",
        "source_dataset": "sector_money_flow",
        "source_sha256": "abc123",
        "generated_at": "2026-06-15T16:00:00Z",
        "schema_version": "sector_money_flow_jsonl_v1",
        "metadata": {"trace": "unit"},
        "sector_etf_volume_confirmed_move": True,
        "sector_etf_dollar_volume": 12345.67,
        "accumulation_distribution_proxy": 0.42,
        "inflow_outflow_proxy": -0.11,
        "flow_confidence": 0.88,
        "flow_support_score": 0.75,
    }

    built = build_sector_money_flow_observation(row)

    assert built["sector_symbol"] == "XLK"
    assert built["idempotency_key"]
    assert built["sector_etf_volume_confirmed_move"] is True
    assert built["sector_etf_dollar_volume"] == 12345.67
    assert built["accumulation_distribution_proxy"] == 0.42
    assert built["inflow_outflow_proxy"] == -0.11
    assert built["metadata"] == {"trace": "unit"}
