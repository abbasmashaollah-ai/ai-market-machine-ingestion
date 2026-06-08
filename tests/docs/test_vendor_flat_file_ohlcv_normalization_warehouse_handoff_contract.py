from __future__ import annotations

from pathlib import Path


def test_vendor_flat_file_ohlcv_normalization_warehouse_handoff_contract_mentions_required_terms() -> None:
    path = Path("docs/vendor_flat_file_ohlcv_normalization_warehouse_handoff_contract.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "normalization and warehouse handoff contract",
        "parsed vendor flat-file ohlcv records",
        "local parser output only",
        "canonical_ohlcv.v1",
        "evidence_type vendor_flat_file_ohlcv",
        "fixture_only remains fixture-only",
        "must not be written as production evidence",
        "validation_status pass",
        "checksum verified",
        "no checksum, no certification",
        "failed validation blocks warehouse handoff",
        "deterministic from vendor, asset_class, symbol, observation_date, dataset_version, source_file_sha256",
        "idempotent_noop",
        "idempotency_conflict",
        "full idempotency key should not be printed",
        "ingestion prepares certified normalized evidence",
        "ai-market-machine-data owns canonical warehouse storage/read apis",
        "ai machine never consumes handoff files directly",
        "ai machine consumes only certified data api/evidence",
        "replay/backtest should use certified canonical ohlcv evidence",
        "manifest/checksum/lineage references",
        "handoff_blocked_fixture_only",
        "handoff_blocked_validation_failed",
        "handoff_blocked_checksum_missing",
        "handoff_blocked_certification_missing",
        "pure local normalizer/handoff builder",
        "no downloader",
        "no vendor activation",
        "no db writes",
        "no scheduler",
        "no ai machine runtime wiring",
        "no vendor calls",
        "no downloads",
        "no ingestion run",
        "no production changes",
        "no secrets committed",
    ]:
        assert needle in text
