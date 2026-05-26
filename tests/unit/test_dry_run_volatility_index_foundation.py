from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class VolatilityIndexFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_volatility_index_foundation as mod

        return mod

    def test_normalized_record_shape(self) -> None:
        from app.normalization.volatility_index import normalize_volatility_index_record

        record = normalize_volatility_index_record(
            {
                "symbol": "VIX",
                "observation_date": "2026-05-21",
                "value": 18.2,
                "source": "sample_fixture",
                "vendor_symbol": "VIX",
                "unit": "index",
                "notes": "deterministic fixture",
            }
        )
        self.assertEqual(record.symbol, "VIX")
        self.assertEqual(str(record.observation_date), "2026-05-21")
        self.assertEqual(record.value, 18.2)
        self.assertEqual(record.source, "sample_fixture")
        self.assertEqual(record.vendor_symbol, "VIX")
        self.assertEqual(record.unit, "index")
        self.assertEqual(record.notes, "deterministic fixture")

    def test_starter_symbols(self) -> None:
        from app.normalization.volatility_index import STARTER_VOLATILITY_INDEX_SYMBOLS

        self.assertEqual(STARTER_VOLATILITY_INDEX_SYMBOLS, ("VIX", "VVIX", "VXN", "RVX"))

    def test_validation_behavior(self) -> None:
        from app.normalization.volatility_index import NormalizedVolatilityIndexRecord, validate_volatility_index_record

        record = NormalizedVolatilityIndexRecord(
            symbol=None,
            observation_date=None,
            value=None,
            source=None,
            vendor_symbol=None,
            unit=None,
        )
        errors = validate_volatility_index_record(record)
        self.assertIn("symbol is required", errors)
        self.assertIn("observation_date is required", errors)
        self.assertIn("value is required", errors)
        self.assertIn("source is required", errors)
        self.assertIn("vendor_symbol is required", errors)
        self.assertIn("unit is required", errors)

    def test_dry_run_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbol_count=4", printed)
        self.assertIn("normalized_count=4", printed)
        self.assertIn("valid_count=4", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("starter_symbols=VIX,VVIX,VXN,RVX", printed)
        self.assertIn("no_vendor_calls=true", printed)
        self.assertIn("no_db_writes=true", printed)

    def test_show_symbols_behavior(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-symbols"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols=['VIX', 'VVIX', 'VXN', 'RVX']", printed)

    def test_show_invalid_behavior(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-invalid"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("invalid_records=()", printed)

    def test_no_vendor_calls(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        self.assertTrue(print_mock.mock_calls)
        source = Path("scripts/dry_run_volatility_index_foundation.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("polygon", source)
        self.assertNotIn("cboe", source)
        self.assertNotIn("fred", source)

    def test_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"):
            mod.main([])

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_volatility_index_foundation.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/volatility_index_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("volatility index foundation", text)
        self.assertIn("dry-run and normalization only", text)
        self.assertIn("vix", text)
        self.assertIn("vvix", text)
        self.assertIn("vxn", text)
        self.assertIn("rvx", text)
        self.assertIn("no vendor calls by default", text)
        self.assertIn("no db writes", text)
        self.assertIn("--show-symbols", text)
        self.assertIn("--show-invalid", text)
        manual_doc = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("scripts.dry_run_volatility_index_foundation", manual_doc)
        self.assertIn("volatility index dry-run foundation", manual_doc)
