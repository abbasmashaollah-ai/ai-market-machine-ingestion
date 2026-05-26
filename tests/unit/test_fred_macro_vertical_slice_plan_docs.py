from __future__ import annotations

import unittest
from pathlib import Path


class FredMacroVerticalSlicePlanDocsTests(unittest.TestCase):
    def test_etf_index_verification_doc(self) -> None:
        text = Path("docs/etf_index_universe_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("candidate_count=22", text)
        self.assertIn("found_count=22", text)
        self.assertIn("missing_count=0", text)
        self.assertIn("proxy_found_count=4", text)
        self.assertIn("proxy_missing_count=0", text)
        self.assertIn("major index labels mapped to etf proxies", text)
        self.assertIn("no vendor calls", text)
        self.assertIn("no db writes", text)

    def test_future_domain_build_order_marks_fred_next(self) -> None:
        text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
        self.assertIn("symbol master", text)
        self.assertIn("etf/index universe expansion", text)
        self.assertIn("fred macro", text)
        self.assertIn("planned next domain after etf/index universe verification", text)

    def test_fred_macro_vertical_slice_plan_doc(self) -> None:
        text = Path("docs/fred_macro_vertical_slice_plan.md").read_text(encoding="utf-8").lower()
        self.assertIn("purpose", text)
        self.assertIn("data repo contract", text)
        self.assertIn("planned vendor adapter", text)
        self.assertIn("normalized macro record shape", text)
        self.assertIn("dgs10", text)
        self.assertIn("dgs2", text)
        self.assertIn("fedfunds", text)
        self.assertIn("cpiau csl".upper().replace(" ", ""), text.upper().replace(" ", ""))
        self.assertIn("unrate", text)
        self.assertIn("writer/store integration is deferred", text)
        self.assertIn("no ai/trading/risk/signal/regime logic", text)
