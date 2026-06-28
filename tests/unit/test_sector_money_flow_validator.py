from app.features.sector_money_flow.sector_money_flow_validator import validate_sector_money_flow_observation


def test_sector_money_flow_validator_rejects_missing_required_fields():
    result = validate_sector_money_flow_observation({})

    assert not result.is_valid
    assert any(error.field == "observation_date" for error in result.errors)


def test_sector_money_flow_validator_rejects_unsupported_claims_and_signals():
    result = validate_sector_money_flow_observation(
        {
            "observation_date": "2026-06-15",
            "sector_symbol": "XLK",
            "source_vendor": "vendor_a",
            "source_dataset": "sector_money_flow",
            "source_sha256": "abc123",
            "generated_at": "2026-06-15T16:00:00Z",
            "schema_version": "sector_money_flow_jsonl_v1",
            "idempotency_key": "custom-key",
            "metadata": {},
            "institutional_flow": 1.0,
            "buy_signal": True,
        }
    )

    assert not result.is_valid
    assert any(error.field == "institutional_flow" for error in result.errors)
    assert any(error.field == "buy_signal" for error in result.errors)
