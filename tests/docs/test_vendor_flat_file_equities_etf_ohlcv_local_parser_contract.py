from __future__ import annotations

from pathlib import Path


def test_vendor_flat_file_equities_etf_ohlcv_local_parser_contract_mentions_required_terms() -> None:
    path = Path("docs/vendor_flat_file_equities_etf_ohlcv_local_parser_contract.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "local parser contract",
        "synthetic polygon-style equities/etf daily ohlcv fixtures",
        "csv fixture path",
        "manifest path next to raw csv",
        "asset_class equities or etfs",
        "expected schema_version `vendor_flat_file_ohlcv.v1`",
        "expected dataset_version `fixture.v1`",
        "no remote urls",
        "no vendor credentials",
        "source_file_sha256 matches actual csv",
        "sha256 verified before parsing",
        "no checksum, no parse",
        "no checksum, no certification",
        "ticker",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "vwap",
        "transactions",
        "adjusted",
        "uppercase symbol",
        "iso yyyy-mm-dd",
        "symbol",
        "observation_date",
        "vendor polygon",
        "manifest_path",
        "certification_status `fixture_only`",
        "reject missing ticker",
        "reject missing date",
        "reject open/high/low/close <= 0",
        "reject high less than low",
        "reject negative volume",
        "reject duplicate symbol/date",
        "warn but allow missing optional vwap",
        "warn but allow missing optional transactions",
        "checksum_mismatch",
        "required_column_missing",
        "invalid_ohlc",
        "duplicate_symbol_date",
        "local files only",
        "no vendor calls",
        "no downloads",
        "no db writes",
        "no scheduler activation",
        "no ai machine runtime wiring",
        "no secrets/tokens/raw provider credentials",
        "parser should be pure function style",
        "runtime downloader comes later",
        "warehouse handoff comes after parser + normalization validation",
        "ai machine consumes only certified data api/evidence",
    ]:
        assert needle in text
