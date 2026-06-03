from pathlib import Path


def test_ingestion_system_current_state_breakdown_doc_covers_required_boundaries() -> None:
    text = Path("docs/ingestion_system_current_state_breakdown.md").read_text(encoding="utf-8")
    required_phrases = [
        "ai-market-machine-ingestion",
        "ai-market-machine-data",
        "AI Machine",
        "ingestion calculates deterministic evidence",
        "data stores and serves certified evidence",
        "AI Machine interprets",
        "app/features",
        "app/sources",
        "app/normalization",
        "app/writers",
        "app/quality",
        "app/state",
        "sector_rotation",
        "breadth",
        "sector_rotation_observations",
        "sector_rotation_daily_summary",
        "SPY",
        "XLC",
        "XLK",
        "XLU",
        "no vendor calls",
        "no DB writes",
        "no scheduler activation",
        "no AI decision logic",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
