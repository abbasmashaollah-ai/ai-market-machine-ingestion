from __future__ import annotations

from datetime import datetime, timezone

from app.ingestion.volatility.observations_producer import build_volatility_observations_dry_run


def _source_record(symbol: str, source_symbol: str, *, value: float = 18.2) -> dict[str, object]:
    return {
        "symbol": symbol,
        "source_symbol": source_symbol,
        "observation_date": "2026-05-21",
        "timestamp": datetime(2026, 5, 21, tzinfo=timezone.utc).isoformat(),
        "value": value,
        "source": "polygon",
    }


def test_produces_canonical_payloads_for_supported_symbols() -> None:
    result = build_volatility_observations_dry_run(
        [
            _source_record("VIX", "I:VIX"),
            _source_record("VVIX", "I:VVIX", value=92.1),
            _source_record("VXN", "I:VXN", value=21.7),
            _source_record("RVX", "I:RVX", value=25.4),
        ]
    )

    assert result.accepted_count == 4
    assert result.rejected_count == 0
    assert len(result.records) == 4
    payload = result.records[0]
    for field in [
        "symbol",
        "index_family",
        "observation_date",
        "timestamp",
        "value",
        "close",
        "source",
        "source_symbol",
        "source_attribution",
        "daily_or_intraday",
        "lineage",
        "quality_status",
        "certification_status",
        "freshness_status",
        "freshness_checked_at",
        "evidence",
    ]:
        assert field in payload
    assert payload["symbol"] == "VIX"
    assert payload["source_symbol"] == "I:VIX"
    assert payload["index_family"] == "volatility_index"
    assert payload["quality_status"] == "pass"
    assert payload["certification_status"] == "pending"
    assert payload["freshness_status"] == "unknown"
    assert payload["daily_or_intraday"] == "daily"


def test_rejects_missing_required_fields() -> None:
    missing_value = build_volatility_observations_dry_run(
        [{"symbol": "VIX", "source_symbol": "I:VIX", "observation_date": "2026-05-21", "timestamp": datetime.now(timezone.utc).isoformat(), "source": "polygon"}]
    )
    missing_timestamp = build_volatility_observations_dry_run(
        [{"symbol": "VIX", "source_symbol": "I:VIX", "observation_date": "2026-05-21", "value": 18.2, "source": "polygon"}]
    )
    missing_source = build_volatility_observations_dry_run(
        [{"symbol": "VIX", "source_symbol": "I:VIX", "observation_date": "2026-05-21", "timestamp": datetime.now(timezone.utc).isoformat(), "value": 18.2}]
    )
    missing_close = build_volatility_observations_dry_run(
        [{"symbol": "VIX", "source_symbol": "I:VIX", "observation_date": "2026-05-21", "timestamp": datetime.now(timezone.utc).isoformat(), "value": None, "source": "polygon"}]
    )

    assert missing_value.rejected_count == 1
    assert missing_value.rejected_records[0]["errors"][0] == "value is required"
    assert missing_timestamp.rejected_count == 1
    assert missing_timestamp.rejected_records[0]["errors"][0] == "timestamp is required"
    assert missing_source.rejected_count == 1
    assert missing_source.rejected_records[0]["errors"][0] == "source is required"
    assert missing_close.rejected_count == 1
    assert "value is required" in missing_close.rejected_records[0]["errors"]


def test_accepts_normalized_records_and_builds_metadata() -> None:
    from app.normalization.volatility_index import normalize_volatility_index_record

    normalized = normalize_volatility_index_record(
        {
            "symbol": "VIX",
            "observation_date": "2026-05-21",
            "value": 18.2,
            "source": "polygon",
            "vendor_symbol": "I:VIX",
            "unit": "index",
        }
    )
    result = build_volatility_observations_dry_run([normalized])

    assert result.accepted_count == 1
    payload = result.records[0]
    assert payload["source_attribution"] == "polygon:I:VIX"
    assert isinstance(payload["lineage"], dict)
    assert isinstance(payload["evidence"], dict)


def test_source_mismatch_is_warned_without_crashing() -> None:
    result = build_volatility_observations_dry_run([_source_record("VIX", "I:VIX")], source_name="other")
    assert result.accepted_count == 1
    assert result.warnings
    assert "source mismatch" in result.warnings[0]


def test_entitlement_error_is_reported_as_warning() -> None:
    record = _source_record("VIX", "I:VIX")
    record["entitlement_error"] = "HTTP 401 unauthorized"
    result = build_volatility_observations_dry_run([record])
    assert result.accepted_count == 1
    assert any("401 unauthorized" in warning for warning in result.warnings)


def test_no_vendor_or_db_clients_are_required() -> None:
    result = build_volatility_observations_dry_run([])
    assert result.accepted_count == 0
    assert result.rejected_count == 0
    assert result.records == ()
