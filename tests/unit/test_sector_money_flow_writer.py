from app.features.sector_money_flow.sector_money_flow_writer import write_sector_money_flow_payloads


def test_sector_money_flow_writer_returns_handoff_shaped_payload_without_db_write():
    result = write_sector_money_flow_payloads(
        [
            {
                "observation_date": "2026-06-15",
                "sector_symbol": "XLF",
                "source_vendor": "vendor_a",
                "source_dataset": "sector_money_flow",
                "source_sha256": "abc123",
                "generated_at": "2026-06-15T16:00:00Z",
                "schema_version": "sector_money_flow_jsonl_v1",
                "metadata": {},
            }
        ]
    )

    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.observation_payloads[0]["sector_symbol"] == "XLF"
    assert result.observation_payloads[0]["idempotency_key"]
