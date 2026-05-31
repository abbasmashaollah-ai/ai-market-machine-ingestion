from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OptionsSourceCandidate:
    source_name: str
    target_datasets: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    lineage_note: str = ""
    quality_note: str = ""
    status: str = "planned"
    priority: int = 0


def build_options_source_candidates() -> tuple[OptionsSourceCandidate, ...]:
    return (
        OptionsSourceCandidate(
            source_name="Polygon",
            target_datasets=("option chains", "option contracts", "open interest", "implied volatility", "put/call volume", "put/call open interest", "expiration metadata"),
            coverage_note="Primary planned source for broad options coverage if approved later.",
            lineage_note="Preserve vendor contract symbol, underlying symbol, expiration date, and strike lineage where available.",
            quality_note="Should align to the approved options normalization contract before any persistence work is considered.",
            status="planned",
            priority=1,
        ),
        OptionsSourceCandidate(
            source_name="Tradier",
            target_datasets=("option chains", "option contracts", "open interest", "implied volatility", "put/call volume", "put/call open interest", "expiration metadata"),
            coverage_note="Complementary planned source for options coverage where Tradier provides suitable endpoints.",
            lineage_note="Preserve vendor identifiers, contract symbol, and underlying mapping in lineage evidence.",
            quality_note="Use only after the options contract is approved and symbol mapping is defined.",
            status="planned",
            priority=2,
        ),
        OptionsSourceCandidate(
            source_name="OCC-derived",
            target_datasets=("option contracts", "open interest", "expiration metadata"),
            coverage_note="Planned derived path from OCC-style sources for contract metadata and open-interest context.",
            lineage_note="Preserve derivation method, source files, and contract mapping in lineage evidence.",
            quality_note="Potentially useful as a normalization backstop once the data-side contract exists.",
            status="planned",
            priority=3,
        ),
        OptionsSourceCandidate(
            source_name="manual_fixture",
            target_datasets=("option chains", "option contracts", "open interest", "implied volatility", "put/call volume", "put/call open interest", "expiration metadata"),
            coverage_note="Test-only deterministic coverage for the planned options record shape.",
            lineage_note="Fixture identity and fixed sample contracts should be preserved in evidence output.",
            quality_note="No live requests; used only to validate planning and normalization boundaries.",
            status="test_only",
            priority=99,
        ),
    )
