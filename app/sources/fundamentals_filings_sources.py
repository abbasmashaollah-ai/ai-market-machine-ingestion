from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FundamentalsFilingsSourceCandidate:
    source_name: str
    supported_record_families: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    lineage_note: str = ""
    quality_note: str = ""
    status: str = "planned"
    priority: int = 0


def build_fundamentals_filings_source_candidates() -> tuple[FundamentalsFilingsSourceCandidate, ...]:
    return (
        FundamentalsFilingsSourceCandidate(
            source_name="SEC",
            supported_record_families=("sec_filing", "company_profile"),
            coverage_note="Primary source for filing disclosures and authoritative company metadata where available.",
            lineage_note="Preserve accession, filing date, form type, and filing URL in lineage evidence.",
            quality_note="Best for authoritative filings; normalization must preserve source identifiers and report coverage gaps explicitly.",
            status="planned",
            priority=1,
        ),
        FundamentalsFilingsSourceCandidate(
            source_name="FMP",
            supported_record_families=("company_profile", "financial_statement", "financial_metric", "earnings_estimate"),
            coverage_note="Planned vendor source for statements, ratios, metrics, and estimates if entitlement is approved.",
            lineage_note="Preserve vendor endpoint, symbol, and report period in lineage evidence.",
            quality_note="Vendor payloads should be normalized deterministically with explicit missing-field reporting.",
            status="planned",
            priority=2,
        ),
        FundamentalsFilingsSourceCandidate(
            source_name="Finnhub",
            supported_record_families=("company_profile", "financial_statement", "financial_metric", "earnings_estimate", "sec_filing"),
            coverage_note="Planned vendor source for broad fundamentals and filing adjacency if access is approved.",
            lineage_note="Preserve vendor source name and request parameters for traceability.",
            quality_note="Use as a complementary source where vendor coverage differs from SEC/FMP.",
            status="planned",
            priority=3,
        ),
        FundamentalsFilingsSourceCandidate(
            source_name="manual_fixture",
            supported_record_families=("company_profile", "financial_statement", "financial_metric", "earnings_estimate", "sec_filing"),
            coverage_note="Test-only deterministic coverage for all planned record families.",
            lineage_note="Fixture identity and fixed sample symbol should be preserved in evidence output.",
            quality_note="No live requests; used only to validate the planning and normalization contract.",
            status="test_only",
            priority=99,
        ),
    )
