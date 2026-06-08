from __future__ import annotations

from pathlib import Path


def test_vendor_flat_file_pipeline_architecture_alignment_mentions_required_terms() -> None:
    path = Path("docs/vendor_flat_file_pipeline_architecture_alignment.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "vendor flat-file pipeline architecture",
        "prevent per-feature vendor downloaders",
        "vendor adapter downloads/acquires once",
        "raw file is stored/stamped",
        "manifest/checksum verifies what arrived",
        "normalizer converts to canonical records",
        "validator checks quality",
        "evidence/certification records why data is trusted",
        "feature builders consume canonical/certified data",
        "ai-market-machine-data owns canonical warehouse/read apis",
        "ai machine consumes certified data api/evidence only",
        "features/prices/download_polygon_flat_files.py",
        "features/breadth/download_polygon_flat_files.py",
        "features/options/download_polygon_flat_files.py",
        "duplicate downloads",
        "inconsistent validation",
        "inconsistent lineage",
        "app/vendors/polygon/flat_files/",
        "app/raw_store/",
        "app/normalization/ohlcv/",
        "app/validation/ohlcv/",
        "app/evidence/",
        "app/features/prices/",
        "app/features/breadth/",
        "app/features/options/",
        "app/writers/",
        "feature folders are vendor-agnostic",
        "canonicaldailybar",
        "canonical ohlcv universe",
        "canonical options chain/snapshot data",
        "canonical macro observations",
        "app/vendor_flat_files/local_ohlcv_parser.py",
        "app/vendors/polygon/flat_files/local_reader.py",
        "app/normalization/ohlcv/polygon_flat_file_normalizer.py",
        "app/validation/ohlcv/daily_bar_validator.py",
        "do not refactor yet without a separate review",
        "normalization/warehouse handoff contract",
        "no downloader",
        "no vendor activation",
        "no db writes",
        "no ai machine runtime wiring",
        "no vendor calls",
        "no downloads",
        "no secrets committed",
    ]:
        assert needle in text
