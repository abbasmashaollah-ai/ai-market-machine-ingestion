from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NewsSentimentSourceCandidate:
    source_name: str
    supported_record_shapes: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    lineage_note: str = ""
    quality_note: str = ""
    status: str = "planned"
    priority: int = 0


def build_news_sentiment_source_candidates() -> tuple[NewsSentimentSourceCandidate, ...]:
    return (
        NewsSentimentSourceCandidate(
            source_name="Finnhub",
            supported_record_shapes=("headline", "article_summary", "sentiment"),
            coverage_note="Planned vendor source for broad news coverage and vendor-provided sentiment if approved.",
            lineage_note="Preserve source ID, publisher, published_at, and related tickers in lineage evidence.",
            quality_note="Should normalize headlines and summaries deterministically with explicit missing-field reporting.",
            status="planned",
            priority=1,
        ),
        NewsSentimentSourceCandidate(
            source_name="FMP",
            supported_record_shapes=("headline", "article_summary", "sentiment"),
            coverage_note="Planned vendor source for market news and related-ticker coverage if approved.",
            lineage_note="Preserve vendor article identifier, publisher, and URL in lineage evidence.",
            quality_note="Use as a complementary news source where coverage differs from Finnhub.",
            status="planned",
            priority=2,
        ),
        NewsSentimentSourceCandidate(
            source_name="Polygon",
            supported_record_shapes=("headline", "article_summary", "sentiment"),
            coverage_note="Planned Polygon news source if available under the approved entitlement.",
            lineage_note="Preserve Polygon story identifiers, timestamps, and ticker attachments in lineage evidence.",
            quality_note="Use only if news entitlement is available and compatible with the slice contract.",
            status="planned",
            priority=3,
        ),
        NewsSentimentSourceCandidate(
            source_name="manual_fixture",
            supported_record_shapes=("headline", "article_summary", "sentiment"),
            coverage_note="Test-only deterministic coverage for the planned news/sentiment record shape.",
            lineage_note="Fixture identity and fixed sample tickers should be preserved in evidence output.",
            quality_note="No live requests; used only to validate planning and normalization boundaries.",
            status="test_only",
            priority=99,
        ),
    )
