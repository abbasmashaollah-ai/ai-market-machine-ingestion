from __future__ import annotations

from datetime import datetime, timezone

from app.ingestion.volatility.observations_producer import build_volatility_observations_dry_run


class FakeWriter:
    def __init__(self) -> None:
        self.records: list[dict[str, object]] = []
        self.calls = 0

    def write(self, records: list[dict[str, object]]) -> dict[str, object]:
        self.calls += 1
        self.records.extend(records)
        return {"written_count": len(records), "status": "success"}


def _fake_source_record(symbol: str, source_symbol: str, *, value: float = 18.2) -> dict[str, object]:
    return {
        "symbol": symbol,
        "source_symbol": source_symbol,
        "observation_date": "2026-05-21",
        "timestamp": datetime(2026, 5, 21, tzinfo=timezone.utc).isoformat(),
        "value": value,
        "source": "polygon",
    }


def _handoff_key(payload: dict[str, object]) -> tuple[object, ...]:
    return (
        payload.get("symbol"),
        payload.get("index_family"),
        payload.get("observation_date"),
        payload.get("source"),
    )


def test_dry_run_payloads_can_be_handed_off_to_a_fake_writer() -> None:
    producer_result = build_volatility_observations_dry_run(
        [
            _fake_source_record("VIX", "I:VIX"),
            _fake_source_record("VVIX", "I:VVIX", value=92.1),
            {"symbol": "VXN", "source_symbol": "I:VXN", "observation_date": "2026-05-21", "source": "polygon"},
        ]
    )

    fake_writer = FakeWriter()
    accepted_records = list(producer_result.records)
    writer_result = fake_writer.write(accepted_records)

    assert producer_result.accepted_count == 2
    assert producer_result.rejected_count == 1
    assert fake_writer.calls == 1
    assert writer_result["written_count"] == 2
    assert len(fake_writer.records) == 2
    for payload in fake_writer.records:
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
        assert _handoff_key(payload) == (
            payload["symbol"],
            payload["index_family"],
            payload["observation_date"],
            payload["source"],
        )


def test_rejected_records_are_not_written() -> None:
    result = build_volatility_observations_dry_run(
        [
            _fake_source_record("VIX", "I:VIX"),
            {"symbol": "VVIX", "source_symbol": "I:VVIX", "observation_date": "2026-05-21", "source": "polygon"},
        ]
    )

    fake_writer = FakeWriter()
    fake_writer.write(list(result.records))

    assert result.rejected_count == 1
    assert len(fake_writer.records) == 1
    assert fake_writer.records[0]["symbol"] == "VIX"


def test_no_real_db_or_vendor_clients_are_used() -> None:
    result = build_volatility_observations_dry_run([_fake_source_record("RVX", "I:RVX", value=25.4)])

    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.records[0]["source"] == "polygon"
    assert result.records[0]["source_symbol"] == "I:RVX"
