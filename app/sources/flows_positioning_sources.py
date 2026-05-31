from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FlowsPositioningSourceCandidate:
    source_name: str
    target_datasets: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    lineage_note: str = ""
    quality_note: str = ""
    status: str = "planned"
    priority: int = 0


def build_flows_positioning_source_candidates() -> tuple[FlowsPositioningSourceCandidate, ...]:
    return (
        FlowsPositioningSourceCandidate(
            source_name="FMP",
            target_datasets=("ETF flows", "fund flows", "short interest", "institutional positioning"),
            coverage_note="Planned vendor source for broad positioning coverage if approved later.",
            lineage_note="Preserve vendor identifiers, symbol mapping, and observation date lineage where available.",
            quality_note="Should align to the approved flows/positioning normalization contract before any persistence work is considered.",
            status="planned",
            priority=1,
        ),
        FlowsPositioningSourceCandidate(
            source_name="FINRA",
            target_datasets=("short interest", "dark pool/off-exchange volume"),
            coverage_note="Planned source for short-interest and off-exchange volume data where publicly available.",
            lineage_note="Preserve publication date, symbol mapping, and source document identifiers in lineage evidence.",
            quality_note="Use only after the flows contract is approved and reporting cadence is defined.",
            status="planned",
            priority=2,
        ),
        FlowsPositioningSourceCandidate(
            source_name="CFTC",
            target_datasets=("CFTC/COT positioning",),
            coverage_note="Planned source for futures positioning and COT-style reports if approved later.",
            lineage_note="Preserve report date, market mapping, and report category lineage where available.",
            quality_note="Potentially authoritative for futures positioning but requires explicit contract approval.",
            status="planned",
            priority=3,
        ),
        FlowsPositioningSourceCandidate(
            source_name="ETF issuer/public datasets",
            target_datasets=("ETF flows", "fund flows"),
            coverage_note="Planned public issuer and fund dataset path for ETF and fund flow context.",
            lineage_note="Preserve issuer dataset identifiers and publication dates in lineage evidence.",
            quality_note="May complement vendor feeds where public data is reliable enough for the contract.",
            status="planned",
            priority=4,
        ),
        FlowsPositioningSourceCandidate(
            source_name="vendor_flow_feed",
            target_datasets=("ETF flows", "fund flows", "institutional positioning"),
            coverage_note="Placeholder for a future vendor flow feed if a specialized product is approved later.",
            lineage_note="Will need explicit vendor and symbol mapping rules before any persistence work is considered.",
            quality_note="Reserved for later planning only; not an approved live adapter.",
            status="planned",
            priority=5,
        ),
        FlowsPositioningSourceCandidate(
            source_name="manual_fixture",
            target_datasets=("ETF flows", "fund flows", "short interest", "institutional positioning", "CFTC/COT positioning", "dark pool/off-exchange volume"),
            coverage_note="Test-only deterministic coverage for the planned flows/positioning record shape.",
            lineage_note="Fixture identity and fixed sample symbols should be preserved in evidence output.",
            quality_note="No live requests; used only to validate planning and normalization boundaries.",
            status="test_only",
            priority=99,
        ),
    )
