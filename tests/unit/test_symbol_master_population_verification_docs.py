from __future__ import annotations

import unittest
from pathlib import Path


class SymbolMasterPopulationVerificationDocsTests(unittest.TestCase):
    def test_verification_doc_covers_population_outcome(self) -> None:
        text = Path("docs/symbol_master_live_population_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("1000 live polygon records fetched", text)
        self.assertIn("1000 normalized", text)
        self.assertIn("1000 valid", text)
        self.assertIn("1000 written", text)
        self.assertIn("coverage_status=pass", text)
        self.assertIn("evidence_status=pass", text)
        self.assertIn("run_status=pass", text)
        self.assertIn("quality_status=pass", text)
        self.assertIn("lineage_status=pass", text)
        self.assertIn("duplicate count 0", text)
        self.assertIn("missing metadata count 0", text)
        self.assertIn("pause", text)
        self.assertIn("pagination and cost planning", text)

    def test_etf_index_plan_covers_boundary_language(self) -> None:
        text = Path("docs/etf_index_universe_expansion_plan.md").read_text(encoding="utf-8").lower()
        self.assertIn("purpose", text)
        self.assertIn("depends on the symbol_master foundation", text)
        self.assertIn("spy", text)
        self.assertIn("sector etfs", text)
        self.assertIn("industry etfs", text)
        self.assertIn("major indexes", text)
        self.assertIn("data repo symbol_master contract", text)
        self.assertIn("no scheduler yet", text)
        self.assertIn("no ai/trading logic", text)
        self.assertIn("preflight", text)
        self.assertIn("runner", text)
        self.assertIn("evidence verification", text)
        self.assertIn("coverage assessment", text)

    def test_future_domain_build_order_mentions_symbol_master_completion(self) -> None:
        text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
        self.assertIn("symbol master", text)
        self.assertIn("started and verified through polygon live population", text)
        self.assertIn("etf/index universe expansion", text)
        self.assertIn("planned next domain", text)
