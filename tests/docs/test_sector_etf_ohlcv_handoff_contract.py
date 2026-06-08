from __future__ import annotations

from pathlib import Path


def test_sector_etf_ohlcv_handoff_contract_mentions_required_terms() -> None:
    path = Path("docs/sector_etf_ohlcv_handoff_contract.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "sector etf ohlcv handoff contract",
        "spy",
        "xlb",
        "xle",
        "xlf",
        "xli",
        "xlk",
        "xlp",
        "xlre",
        "xlu",
        "xlv",
        "xly",
        "xlc",
        "symbol",
        "observation_date",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "timeframe",
        "adjusted",
        "source",
        "dataset_version",
        "schema_version",
        "validation_status",
        "certification_status",
        "lineage_id",
        "source_file_sha256",
        "idempotency key",
        "fixture-only records are not production eligible",
        "approved non-fixture source",
        "failed validation blocks handoff",
        "ingestion produces handoff records only",
        "data accepts, stores, and certifies",
        "ingestion does not write production db",
        "data does not call vendors",
        "core does not consume raw handoff files",
        "no vendor calls",
        "no downloads",
        "no db writes",
        "no scheduler activation",
        "no full secret or idempotency exposure",
        "no raw vendor data committed",
        "pure local sector etf ohlcv handoff dry-run",
        "synthetic or approved local records only",
    ]:
        assert needle in text, needle
