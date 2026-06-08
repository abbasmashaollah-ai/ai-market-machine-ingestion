from __future__ import annotations

from pathlib import Path


def test_sector_etf_ohlcv_handoff_dry_run_doc_mentions_required_terms() -> None:
    path = Path("docs/sector_etf_ohlcv_handoff_dry_run.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "sector etf ohlcv handoff dry run",
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
        "synthetic or approved local records only",
        "safe summary only",
        "universe_count",
        "records_generated",
        "symbols_ready",
        "symbols_missing",
        "validation_status",
        "certification_status",
        "production_eligible",
        "fixture_only",
        "db_write_attempted",
        "vendor_call_attempted",
        "download_attempted",
        "scheduler_activation_attempted",
        "idempotency_key_prefixes",
        "never writes to db",
        "never calls vendors",
        "never downloads files",
        "never activates schedulers",
        "never prints full idempotency keys",
        "ingestion produces handoff records only",
        "data accepts, stores, and certifies",
        "core does not consume raw handoff files",
    ]:
        assert needle in text, needle
