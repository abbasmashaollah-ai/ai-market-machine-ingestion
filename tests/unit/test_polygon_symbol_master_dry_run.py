from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class PolygonSymbolMasterDryRunTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_polygon_symbol_master as mod

        return mod

    def test_default_dry_run_uses_safe_limit(self) -> None:
        mod = self._module()
        with patch.object(mod, "_normalize_records", wraps=mod._normalize_records) as normalize_mock, patch(
            "builtins.print"
        ) as print_mock, patch("sys.argv", ["dry_run_polygon_symbol_master.py"]):
            mod.main()

        normalize_mock.assert_called_once()
        kwargs = normalize_mock.call_args.kwargs
        self.assertEqual(kwargs["limit"], 25)
        self.assertTrue(kwargs["active_only"])
        self.assertIsNone(kwargs["exchange"])
        self.assertIsNone(kwargs["asset_type"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("limit=25", printed)
        self.assertIn("max_records=1000", printed)
        self.assertIn("active_filter=True", printed)

    def test_max_records_block(self) -> None:
        mod = self._module()
        with patch.object(mod, "_normalize_records", return_value=[object()] * 1001), patch.dict(
            "os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True
        ), patch("sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check", "--max-records", "1000"]):
            with self.assertRaisesRegex(RuntimeError, "max-records guardrail"):
                mod.main()

    def test_confirm_write_blocked_when_over_limit(self) -> None:
        mod = self._module()
        with patch.object(mod, "_normalize_records", return_value=[object()] * 1001), patch.dict(
            "os.environ",
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://example"},
            clear=True,
        ), patch("sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check", "--confirm-write", "--max-records", "1000"]):
            with self.assertRaisesRegex(RuntimeError, "max-records guardrail"):
                mod.main()

    def test_filters_passed_to_adapter(self) -> None:
        mod = self._module()
        from app.normalization.symbol_master import NormalizedSymbolMasterRecord

        adapter = Mock()
        adapter.fetch_reference_tickers.return_value = [{"ticker": "AAPL", "active": True, "primary_exchange": "XNAS", "type": "CS"}]
        adapter.map_reference_ticker.return_value = NormalizedSymbolMasterRecord(
            symbol="AAPL",
            active=True,
            vendor="polygon",
            vendor_symbol="AAPL",
            exchange="XNAS",
            asset_type="equity",
        )
        with patch.dict(
            "os.environ",
            {"POLYGON_API_KEY": "polygon-secret"},
            clear=True,
        ), patch.object(mod, "_build_adapter", return_value=adapter), patch("builtins.print"), patch(
            "sys.argv",
            [
                "dry_run_polygon_symbol_master.py",
                "--live-check",
                "--exchange",
                "XNAS",
                "--asset-type",
                "equity",
                "--include-inactive",
            ],
        ):
            mod.main()

        adapter.fetch_reference_tickers.assert_called_once_with(active=False, limit=25)

    def test_confirm_write_within_limit_calls_writer(self) -> None:
        mod = self._module()
        from app.normalization.symbol_master import NormalizedSymbolMasterRecord

        adapter = Mock()
        adapter.fetch_reference_tickers.return_value = [{"ticker": "AAPL", "active": True, "primary_exchange": "XNAS", "type": "CS"}]
        normalized_record = NormalizedSymbolMasterRecord(
            symbol="AAPL",
            active=True,
            vendor="polygon",
            vendor_symbol="AAPL",
            exchange="XNAS",
            asset_type="equity",
        )
        adapter.map_reference_ticker.return_value = normalized_record
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "skipped_count": 0, "succeeded": True})()
        connection = Mock()
        with patch.dict(
            "os.environ",
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://example"},
            clear=True,
        ), patch.object(mod, "_build_adapter", return_value=adapter), patch.object(mod, "_open_connection", return_value=connection), patch.object(
            mod, "SymbolMasterWriter", return_value=writer
        ), patch("builtins.print"), patch(
            "sys.argv",
            ["dry_run_polygon_symbol_master.py", "--live-check", "--confirm-write"],
        ):
            mod.main()

        writer.write.assert_called_once()

    def test_record_flags_require_database_url(self) -> None:
        mod = self._module()
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch(
            "sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check", "--record-run"]
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_polygon_symbol_master.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("ai_market_machine_data", text)
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertIn("SymbolMasterWriter", text)

    def test_docs_cover_command(self) -> None:
        text = Path("docs/polygon_symbol_master_dry_run.md").read_text(encoding="utf-8").lower()
        self.assertIn("limit", text)
        self.assertIn("max-records", text)
        self.assertIn("exchange", text)
        self.assertIn("asset-type", text)
        self.assertIn("active-only", text)
        self.assertIn("include-inactive", text)
