from pathlib import Path


def test_sector_rotation_readme_covers_contract_and_universe() -> None:
    text = Path("app/features/sector_rotation/README.md").read_text(encoding="utf-8")
    required_phrases = [
        "sector_rotation",
        "SPY",
        "XLC",
        "XLK",
        "XLU",
        "sector_rotation_observations",
        "sector_rotation_daily_summary",
        "risk_on_leadership_score",
        "defensive_leadership_score",
        "1. sector universe + dataclasses",
        "11. scheduler activation last",
        "no vendor calls",
        "no DB writes",
        "no scheduler activation",
        "no AI regime logic",
        "no judge posture",
        "no trading logic",
        "no capital logic",
        "no portfolio logic",
        "no AI confidence logic",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"

