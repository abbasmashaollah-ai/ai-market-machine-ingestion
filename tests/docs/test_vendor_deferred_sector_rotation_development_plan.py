from pathlib import Path


def test_vendor_deferred_sector_rotation_development_plan_covers_deferred_path_and_boundaries() -> None:
    text = Path("docs/vendor_deferred_sector_rotation_development_plan.md").read_text(encoding="utf-8")
    required_phrases = [
        "vendor subscription intentionally deferred",
        "no paid vendor activation",
        "sector_rotation",
        "XLC",
        "XLK",
        "XLU",
        "fixture OHLCV histories",
        "production-shaped payloads",
        "dry-run",
        "real writer/persistence remains blocked",
        "scheduler activation remains blocked",
        "AI Machine integration",
        "certified OHLCV coverage",
        "no DB writes",
        "no vendor calls",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
