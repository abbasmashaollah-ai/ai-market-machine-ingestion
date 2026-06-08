from __future__ import annotations

from pathlib import Path


def test_vendor_flat_file_equities_etf_ohlcv_contract_mentions_required_terms() -> None:
    path = Path("docs/vendor_flat_file_equities_etf_ohlcv_contract.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "vendor flat-file contract",
        "equities and etfs",
        "polygon-style flat files",
        "daily ohlcv",
        "spy",
        "qqq",
        "iwm",
        "dia",
        "xlc",
        "xly",
        "xlp",
        "xle",
        "xlf",
        "xlv",
        "xli",
        "xlb",
        "xlre",
        "xlk",
        "xlu",
        "no options/futures implementation yet",
        "no paid vendor activation",
        "no large downloads",
        "data/vendor/polygon/flatfiles/equities/daily/yyyy/mm/dd/",
        "data/vendor/polygon/flatfiles/etfs/daily/yyyy/mm/dd/",
        "manifest.json",
        "source_file_sha256",
        "sha256 required",
        "no checksum, no certification",
        "ticker",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "symbol",
        "observation_date",
        "duplicate symbol/date rows",
        "checksum mismatch blocks certification",
        "ai-market-machine-data owns canonical warehouse storage/read apis",
        "ai machine consumes only certified data api/evidence",
        "deterministic backtests",
        "manifest/checksum/lineage references",
        "options eod chain contract later",
        "futures eod contract later",
        "daily download scheduler only after contracts/fixtures/parser/validation are complete",
        "no vendor calls",
        "no downloads",
        "no db writes",
        "no ingestion run",
        "no scheduler activation",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
    ]:
        assert needle in text
