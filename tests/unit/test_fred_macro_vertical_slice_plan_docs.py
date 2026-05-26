from __future__ import annotations

import unittest
from pathlib import Path


class FredMacroVerticalSlicePlanDocsTests(unittest.TestCase):
    def test_fred_macro_live_population_verification_doc(self) -> None:
        text = Path("docs/fred_macro_live_population_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("series_count=5", text)
        self.assertIn("total_rows=25", text)
        self.assertIn("dgs10=5", text)
        self.assertIn("dgs2=5", text)
        self.assertIn("fedfunds=5", text)
        self.assertIn("cpiau csl".replace(" ", ""), text.replace(" ", ""))
        self.assertIn("unrate=5", text)
        self.assertIn("evidence_status=pass", text)
        self.assertIn("no db writes", text)
        self.assertIn("no vendor calls", text)

    def test_future_domain_build_order_marks_fred_verified_and_volatility_next(self) -> None:
        text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
        self.assertIn("symbol master", text)
        self.assertIn("etf/index universe expansion", text)
        self.assertIn("fred macro", text)
        self.assertIn("verified through live population evidence", text)
        self.assertIn("volatility indexes", text)
        self.assertIn("planned next domain after fred macro verification", text)

    def test_volatility_index_vertical_slice_plan_doc(self) -> None:
        text = Path("docs/volatility_index_vertical_slice_plan.md").read_text(encoding="utf-8").lower()
        self.assertIn("purpose", text)
        self.assertIn("data repo contract", text)
        self.assertIn("starter symbols", text)
        self.assertIn("vix", text)
        self.assertIn("vvix", text)
        self.assertIn("vxn", text)
        self.assertIn("rvx", text)
        self.assertIn("normalized record shape proposal", text)
        self.assertIn("vendor_symbol", text)
        self.assertIn("preflight/runner/evidence pattern", text)
        self.assertIn("no ai/trading/risk/signal/regime/portfolio logic", text)
