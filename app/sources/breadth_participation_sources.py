from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BreadthParticipationSourceCandidate:
    source_name: str
    target_metrics: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    lineage_note: str = ""
    quality_note: str = ""
    status: str = "planned"
    priority: int = 0


def build_breadth_participation_source_candidates() -> tuple[BreadthParticipationSourceCandidate, ...]:
    return (
        BreadthParticipationSourceCandidate(
            source_name="vendor_breadth_feed",
            target_metrics=("advance/decline counts", "new highs/new lows", "percent above moving averages", "up-volume/down-volume", "sector participation", "index/universe breadth"),
            coverage_note="Planned vendor feed for breadth metrics if an approved market data source exists.",
            lineage_note="Preserve source identifiers, universe mapping, and observation date in lineage evidence.",
            quality_note="Use only after the breadth contract is approved and metric normalization is defined.",
            status="planned",
            priority=1,
        ),
        BreadthParticipationSourceCandidate(
            source_name="exchange_breadth_feed",
            target_metrics=("advance/decline counts", "new highs/new lows", "sector participation", "index/universe breadth"),
            coverage_note="Planned exchange breadth feed where direct exchange data is available.",
            lineage_note="Preserve exchange identifiers and universe context in lineage evidence.",
            quality_note="Potentially authoritative for exchange-level breadth metrics but requires explicit approval.",
            status="planned",
            priority=2,
        ),
        BreadthParticipationSourceCandidate(
            source_name="derived_from_ohlcv",
            target_metrics=("percent above moving averages", "up-volume/down-volume", "index/universe breadth"),
            coverage_note="Planned derived path from approved OHLCV data once the OHLCV contract exists.",
            lineage_note="Preserve source OHLCV universe, aggregation window, and derivation method in lineage evidence.",
            quality_note="Should only be used after the shared OHLCV contract is approved.",
            status="planned",
            priority=3,
        ),
        BreadthParticipationSourceCandidate(
            source_name="manual_fixture",
            target_metrics=("advance/decline counts", "new highs/new lows", "percent above moving averages", "up-volume/down-volume", "sector participation", "index/universe breadth"),
            coverage_note="Test-only deterministic coverage for the planned breadth/participation record shape.",
            lineage_note="Fixture identity and fixed sample universe should be preserved in evidence output.",
            quality_note="No live requests; used only to validate planning and normalization boundaries.",
            status="test_only",
            priority=99,
        ),
    )
