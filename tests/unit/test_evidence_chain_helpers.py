from __future__ import annotations

import unittest
from datetime import date

from scripts.evidence_chain_helpers import evidence_status_from_counts, status_from_requirement


class EvidenceChainHelpersTests(unittest.TestCase):
    def test_status_from_requirement_shared_semantics(self) -> None:
        self.assertEqual(status_from_requirement(required=True, present=True), "PASS")
        self.assertEqual(status_from_requirement(required=True, present=False), "FAIL")
        self.assertEqual(status_from_requirement(required=False, present=False), "PASS")
        self.assertEqual(status_from_requirement(required=False, present=True), "WARN")

    def test_evidence_status_from_counts_shared_semantics(self) -> None:
        self.assertEqual(
            evidence_status_from_counts(
                canonical_count=0,
                run_count=0,
                quality_count=0,
                lineage_count=0,
                missing_dates=[],
            ),
            "missing",
        )
        self.assertEqual(
            evidence_status_from_counts(
                canonical_count=2,
                run_count=1,
                quality_count=1,
                lineage_count=1,
                missing_dates=[],
            ),
            "complete",
        )
        self.assertEqual(
            evidence_status_from_counts(
                canonical_count=2,
                run_count=0,
                quality_count=1,
                lineage_count=1,
                missing_dates=[date(2026, 1, 2)],
            ),
            "partial",
        )
