from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CrossAssetOhlcvSourceCandidate:
    source_name: str
    target_groups: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    lineage_note: str = ""
    quality_note: str = ""
    status: str = "planned"
    priority: int = 0


def build_cross_asset_ohlcv_source_candidates() -> tuple[CrossAssetOhlcvSourceCandidate, ...]:
    return (
        CrossAssetOhlcvSourceCandidate(
            source_name="Polygon",
            target_groups=("bonds/rates proxies", "DXY / dollar index proxy", "commodities", "crypto", "FX"),
            coverage_note="Primary planned source for broad cross-asset OHLCV coverage if approved later.",
            lineage_note="Preserve vendor symbol mapping and timeframe lineage for each normalized OHLCV record.",
            quality_note="Should align to the existing OHLCV normalization and writer contract once approved.",
            status="planned",
            priority=1,
        ),
        CrossAssetOhlcvSourceCandidate(
            source_name="FMP",
            target_groups=("bonds/rates proxies", "DXY / dollar index proxy", "commodities", "crypto", "FX"),
            coverage_note="Complementary planned source for cross-asset OHLCV coverage where FMP provides suitable symbols.",
            lineage_note="Preserve vendor symbol mapping, source, and market date lineage for each record.",
            quality_note="Use only after the symbol/asset scope is approved and the shared OHLCV contract is ready.",
            status="planned",
            priority=2,
        ),
        CrossAssetOhlcvSourceCandidate(
            source_name="future_specialty_fx_crypto_source",
            target_groups=("FX", "crypto"),
            coverage_note="Placeholder for a future specialty FX/crypto source once asset scope is approved.",
            lineage_note="Will need explicit vendor and symbol mapping rules before any persistence work is considered.",
            quality_note="Reserved for later planning only; not an approved live adapter.",
            status="planned",
            priority=3,
        ),
        CrossAssetOhlcvSourceCandidate(
            source_name="manual_fixture",
            target_groups=("bonds/rates proxies", "DXY / dollar index proxy", "commodities", "crypto", "FX"),
            coverage_note="Test-only deterministic coverage for the planned cross-asset OHLCV slice.",
            lineage_note="Fixture identity and fixed sample symbols should be preserved in evidence output.",
            quality_note="No live requests; used only to validate planning and normalization boundaries.",
            status="test_only",
            priority=99,
        ),
    )
