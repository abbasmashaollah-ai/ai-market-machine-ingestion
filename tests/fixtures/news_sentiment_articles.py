from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _article(article_id, published_at, source, headline, summary, symbols, category, sentiment_score, relevance_score, impact_score):
    return {
        "article_id": article_id,
        "published_at": published_at,
        "source": source,
        "headline": headline,
        "summary": summary,
        "symbols": list(symbols),
        "category": category,
        "sentiment_score": sentiment_score,
        "relevance_score": relevance_score,
        "impact_score": impact_score,
    }


def _iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def build_news_sentiment_articles_scenario(name: str):
    base = datetime(2026, 1, 15, 15, 30, tzinfo=timezone.utc)
    if name == "positive_macro":
        return [
            _article("ns-1", _iso(base - timedelta(hours=2)), "fixture_news", "Fed signals easier policy", "Macro tone improves.", ["SPY", "QQQ"], "FED", 0.8, 0.9, 0.85),
            _article("ns-2", _iso(base - timedelta(hours=3)), "fixture_news", "Inflation eases", "CPI print softer than expected.", ["SPY"], "MACRO", 0.6, 0.8, 0.7),
            _article("ns-3", _iso(base - timedelta(hours=4)), "fixture_news", "Earnings beats lift sentiment", "Large-cap results beat estimates.", ["AAPL", "MSFT"], "EARNINGS", 0.55, 0.75, 0.6),
        ]
    if name == "negative_macro":
        return [
            _article("ns-4", _iso(base - timedelta(hours=2)), "fixture_news", "Fed stays restrictive", "Policy remains tight.", ["SPY", "TLT"], "FED", -0.75, 0.9, 0.9),
            _article("ns-5", _iso(base - timedelta(hours=3)), "fixture_news", "Inflation surprise higher", "CPI accelerates.", ["SPY"], "MACRO", -0.65, 0.8, 0.8),
            _article("ns-6", _iso(base - timedelta(hours=5)), "fixture_news", "Risk aversion hits cyclicals", "Sector pressure broadens.", ["XLY", "XLF"], "SECTOR", -0.45, 0.7, 0.55),
        ]
    if name == "mixed_market":
        return [
            _article("ns-7", _iso(base - timedelta(hours=2)), "fixture_news", "Fed remains data dependent", "Neutral policy tone.", ["SPY"], "FED", 0.05, 0.7, 0.4),
            _article("ns-8", _iso(base - timedelta(hours=3)), "fixture_news", "Some earnings beat", "Company updates are mixed.", ["AAPL"], "EARNINGS", 0.35, 0.65, 0.5),
            _article("ns-9", _iso(base - timedelta(hours=4)), "fixture_news", "Another company warns", "Guidance offset by other names.", ["MSFT"], "COMPANY", -0.3, 0.6, 0.45),
            _article("ns-10", _iso(base - timedelta(hours=6)), "fixture_news", "Sector rotation continues", "Leadership rotates without conviction.", ["XLE", "XLF"], "SECTOR", 0.0, 0.5, 0.3),
        ]
    if name == "high_impact_negative":
        return [
            _article("ns-11", _iso(base - timedelta(hours=1)), "fixture_news", "Emergency Fed surprise", "Sharp repricing in rates.", ["SPY", "TLT"], "FED", -0.9, 0.95, 0.95),
            _article("ns-12", _iso(base - timedelta(hours=2)), "fixture_news", "Geopolitical shock escalates", "Risk assets weaken.", ["SPY", "QQQ", "IWM"], "GEOPOLITICAL", -0.85, 0.9, 0.9),
            _article("ns-13", _iso(base - timedelta(hours=3)), "fixture_news", "Volatility spikes", "Market stress broadens.", ["VIX"], "VOLATILITY", -0.7, 0.85, 0.92),
        ]
    if name == "high_impact_positive":
        return [
            _article("ns-14", _iso(base - timedelta(hours=1)), "fixture_news", "Fed turns supportive", "Policy tone improves materially.", ["SPY", "QQQ"], "FED", 0.9, 0.95, 0.95),
            _article("ns-15", _iso(base - timedelta(hours=2)), "fixture_news", "Strong earnings wave", "Beat and raise across megacaps.", ["AAPL", "MSFT"], "EARNINGS", 0.85, 0.9, 0.92),
            _article("ns-16", _iso(base - timedelta(hours=3)), "fixture_news", "Cyclicals rally", "Sector breadth improves.", ["XLY", "XLF"], "SECTOR", 0.7, 0.8, 0.8),
        ]
    if name == "low_signal":
        return [
            _article("ns-17", _iso(base - timedelta(hours=2)), "fixture_news", "Small update", "Little market impact.", ["SPY"], "OTHER", 0.02, 0.15, 0.1),
            _article("ns-18", _iso(base - timedelta(hours=4)), "fixture_news", "Another small update", "No clear direction.", ["QQQ"], "OTHER", -0.01, 0.1, 0.05),
        ]
    raise ValueError(f"Unknown scenario: {name}")
