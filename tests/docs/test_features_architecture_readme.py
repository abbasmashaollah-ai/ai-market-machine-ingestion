from pathlib import Path


def test_app_features_readme_covers_feature_boundary() -> None:
    text = Path("app/features/README.md").read_text(encoding="utf-8")
    required_phrases = [
        "app/features",
        "deterministic evidence",
        "reader -> engine/calculator -> observation_builder -> validator -> writer -> job",
        "vendor calls",
        "database writes",
        "scheduler activation",
        "AI regime logic",
        "buy/sell logic",
        "capital allocation",
        "portfolio logic",
        "AI confidence logic",
        "app/vendors/",
        "app/sources/",
        "app/normalization/",
        "app/writers/",
        "app/quality/",
        "app/state/",
        "prices",
        "universe",
        "breadth",
        "sector_rotation",
        "volatility",
        "options",
        "macro_liquidity",
        "flows_positioning",
        "fundamentals",
        "earnings",
        "news_sentiment",
        "event_calendar",
        "cross_asset",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"

