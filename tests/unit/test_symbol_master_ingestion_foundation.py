from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class SymbolMasterIngestionFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_symbol_master_ingestion as mod

        return mod

    def test_normalized_record_shape(self) -> None:
        mod = self._module()
        source = mod.DEFAULT_SAMPLE_SOURCE[0]
        normalized = mod.normalize_symbol_record(source)
        self.assertEqual(normalized.symbol, "AAPL")
        self.assertTrue(normalized.active)
        self.assertEqual(normalized.vendor, "fmp")
        self.assertEqual(normalized.source, "AAPL")
        self.assertEqual(normalized.asset_class, "equity")
        self.assertEqual(normalized.exchange, "NASDAQ")
        self.assertEqual(normalized.normalization_version, "symbol_master.v1")

    def test_validation_behavior(self) -> None:
        mod = self._module()
        source = mod.SymbolMasterSourceRecord(symbol=None, active=None, vendor=" ", vendor_symbol=" ", asset_type=" ", exchange=" ")
        errors = mod.validate_source_record(source)
        self.assertIn("symbol is required", errors)
        self.assertIn("active is required", errors)
        self.assertIn("vendor cannot be empty", errors)
        self.assertIn("vendor_symbol cannot be empty", errors)
        self.assertIn("asset_type cannot be empty", errors)
        self.assertIn("exchange cannot be empty", errors)
        normalized = mod.normalize_symbol_record(source)
        self.assertIn("symbol is required", mod.validate_symbol_record(normalized))

    def test_dry_run_command(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["dry_run_symbol_master_ingestion.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("input_count=3", printed)
        self.assertIn("normalized_count=3", printed)
        self.assertIn("valid_count=3", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("dry_run=True", printed)

    def test_no_db_writes_or_vendor_calls(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_dry_run_summary", wraps=mod.build_dry_run_summary) as summary_mock, patch(
            "builtins.print"
        ), patch("sys.argv", ["dry_run_symbol_master_ingestion.py"]):
            mod.main()

        summary_mock.assert_called_once()

    def test_source_has_no_forbidden_imports(self) -> None:
        source = Path("scripts/dry_run_symbol_master_ingestion.py").read_text(encoding="utf-8")
        self.assertNotIn("from fastapi", source.lower())
        self.assertNotIn("apirouter", source.lower())
        self.assertNotIn("alembic", source.lower())
        self.assertNotIn("requests", source.lower())
        self.assertNotIn("httpx", source.lower())
        self.assertNotIn("ai_market_machine_data", source)
        self.assertNotIn("open_connection", source)
        self.assertNotIn("database_url", source.lower())
        self.assertNotIn("commit(", source.lower())

    def test_docs_cover_foundation(self) -> None:
        text = Path("docs/symbol_master_ingestion_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("symbol master ingestion foundation", text)
        self.assertIn("dry-run", text)
        self.assertIn("call vendors", text)
        self.assertIn("database", text)
        self.assertIn("schema contracts", text)

    def test_manual_inventory_includes_symbol_master_command(self) -> None:
        import scripts.verify_manual_ingestion_commands as inventory

        self.assertIn("scripts.dry_run_symbol_master_ingestion", inventory.MODULES)
