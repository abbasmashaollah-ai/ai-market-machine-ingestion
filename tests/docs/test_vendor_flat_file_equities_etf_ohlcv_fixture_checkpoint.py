from __future__ import annotations

from pathlib import Path


def test_vendor_flat_file_equities_etf_ohlcv_fixture_checkpoint_mentions_required_terms() -> None:
    path = Path("docs/vendor_flat_file_equities_etf_ohlcv_fixture_checkpoint.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "tiny synthetic fixture samples",
        "equities and etf daily ohlcv",
        "manifest next to raw files",
        "sha256 is verified",
        "no checksum, no certification",
        "validator exists",
        "fixtures are not real vendor data",
        "fixtures are not production evidence",
        "no runtime adapter",
        "no downloader",
        "no vendor calls",
        "no downloads",
        "no db writes",
        "no ingestion run",
        "no scheduler activation",
        "no ai machine runtime wiring",
        "local parser contract, not runtime downloader",
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
