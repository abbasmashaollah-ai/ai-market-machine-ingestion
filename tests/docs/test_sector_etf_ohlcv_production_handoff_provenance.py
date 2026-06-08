from __future__ import annotations

from pathlib import Path


def test_sector_etf_ohlcv_production_handoff_provenance_doc_contains_required_boundary() -> None:
    text = Path("docs/sector_etf_ohlcv_production_handoff_provenance.md").read_text(encoding="utf-8")

    assert "approved vendor-produced records only" in text
    assert "synthetic fixtures" in text
    assert "dry-run artifacts" in text
    assert "fixture-only records" in text
    assert "SPY" in text
    for symbol in ["XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"]:
        assert symbol in text
    for field in [
        "symbol",
        "observation_date or timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "timeframe",
        "adjusted",
        "source or vendor",
        "dataset_version",
        "schema_version",
        "validation_status",
        "certification_status",
        "lineage_id",
        "checksum or source_file_sha256",
        "deterministic idempotency_key",
    ]:
        assert field in text
    assert "validation_status = PASS" in text
    assert "certification_status not equal to FIXTURE_ONLY" in text
    assert "APPROVE SECTOR ETF OHLCV PRODUCTION HANDOFF GENERATION" in text
    assert "sector rotation production activation phrase must not be reused" in text
    assert "test-db approval phrase must not be accepted" in text
    assert "vendor calls" in text
    assert "downloads" in text
    assert "exports" in text
    assert "live ingestion" in text
    assert "scheduler activation" in text
    assert "DB writes" in text
    assert "ingestion produces approved vendor handoff records" in text
    assert "data repo accepts, stores, and certifies" in text
    assert "core interprets deterministic evidence" in text
    assert "read-only vendor connectivity/provenance preflight" in text
    assert "not production export" in text
