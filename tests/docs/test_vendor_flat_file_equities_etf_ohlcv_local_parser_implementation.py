from __future__ import annotations

from pathlib import Path


def test_vendor_flat_file_equities_etf_ohlcv_local_parser_implementation_mentions_required_terms() -> None:
    path = Path("docs/vendor_flat_file_equities_etf_ohlcv_local_parser_implementation.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "local parser implementation",
        "synthetic fixtures only",
        "no runtime adapter",
        "no downloader",
        "no vendor calls",
        "no downloads",
        "no db writes",
        "no scheduler activation",
        "no ai machine runtime wiring",
        "parser output is not production evidence",
        "warehouse handoff comes later",
        "local files only",
        "pure function style where possible",
        "no env vars read",
        "no requests/http/vendor sdk imports",
        "no db or writer imports",
        "no output files written",
        "the parser consumes fixture csv + adjacent manifest",
        "the parser validates checksum before parsing",
        "the parser normalizes rows into the documented contract shape",
        "ai machine consumes only certified data api/evidence",
    ]:
        assert needle in text
