from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class PolygonSymbolMasterDryRunTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_polygon_symbol_master as mod

        return mod

    def test_sample_mode_no_vendor_calls(self) -> None:
        mod = self._module()
        with patch.object(mod, "PolygonSymbolMasterAdapter") as adapter_cls, patch("builtins.print") as print_mock:
            adapter = adapter_cls.return_value
            adapter.build_sample_reference_payloads.return_value = [
                {"ticker": "AAPL", "active": True, "delisted": False, "primary_exchange": "XNAS", "type": "CS", "currency": "USD"}
            ]
            adapter.map_reference_ticker.return_value = type(
                "Record",
                (),
                {"symbol": "AAPL", "active": True, "vendor": "polygon", "vendor_symbol": "AAPL", "exchange": "XNAS", "asset_type": "equity"},
            )()
            with patch("sys.argv", ["dry_run_polygon_symbol_master.py"]):
                mod.main()

        adapter.fetch_reference_tickers_raw.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("vendor=polygon", printed)
        self.assertIn("dry_run=True", printed)
        self.assertIn("input_count=1", printed)

    def test_live_check_requires_polygon_key(self) -> None:
        mod = self._module()
        with patch.dict("os.environ", {}, clear=True), patch("sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check"]):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_live_check_uses_adapter_when_key_present(self) -> None:
        mod = self._module()
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonSymbolMasterAdapter"
        ) as adapter_cls, patch("builtins.print"):
            adapter = adapter_cls.return_value
            adapter.fetch_reference_tickers_raw.return_value = [
                {"ticker": "AAPL", "active": True, "delisted": False, "primary_exchange": "XNAS", "type": "CS", "currency": "USD"}
            ]
            adapter.map_reference_ticker.return_value = type(
                "Record",
                (),
                {"symbol": "AAPL", "active": True, "vendor": "polygon", "vendor_symbol": "AAPL", "exchange": "XNAS", "asset_type": "equity"},
            )()
            with patch("sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check"]):
                mod.main()

        adapter.fetch_reference_tickers_raw.assert_called_once()

    def test_active_delisted_mapping(self) -> None:
        from app.vendors.polygon_symbol_master import PolygonSymbolMasterAdapter, PolygonSymbolMasterSourceConfig

        adapter = PolygonSymbolMasterAdapter(PolygonSymbolMasterSourceConfig())
        active = adapter.map_reference_ticker(
            {"ticker": "AAPL", "active": True, "delisted": False, "primary_exchange": "XNAS", "type": "CS", "name": "Apple Inc.", "currency": "USD"}
        )
        inactive = adapter.map_reference_ticker(
            {"ticker": "XYZ", "active": False, "delisted": True, "primary_exchange": "XNAS", "type": "CS", "name": "Example", "currency": "USD"}
        )
        self.assertTrue(active.active)
        self.assertFalse(inactive.active)
        self.assertEqual(active.asset_type, "equity")

    def test_sanitized_error_handling(self) -> None:
        from app.vendors.polygon_symbol_master import PolygonSymbolMasterAdapter, PolygonSymbolMasterSourceConfig

        adapter = PolygonSymbolMasterAdapter(PolygonSymbolMasterSourceConfig(api_key="polygon-secret"))
        with patch.object(adapter, "_client_or_build", side_effect=RuntimeError("POLYGON_API_KEY missing")):
            with self.assertRaises(RuntimeError) as ctx:
                adapter.fetch_reference_tickers_raw()

        self.assertNotIn("polygon-secret", str(ctx.exception))
        self.assertNotIn("POLYGON_API_KEY", str(ctx.exception))

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_polygon_symbol_master.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("ai_market_machine_data", text)
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("open_connection", text)
        self.assertNotIn("commit(", text.lower())
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_cover_command(self) -> None:
        text = Path("docs/polygon_symbol_master_dry_run.md").read_text(encoding="utf-8").lower()
        self.assertIn("polygon symbol master dry run", text)
        self.assertIn("dry_run=true", text)
        self.assertIn("live-check", text)
