from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class PolygonSymbolMasterTargetedLookupTests(unittest.TestCase):
    def _module(self):
        import scripts.fetch_polygon_symbol_master_by_symbols as mod

        return mod

    def _spy_payload(self) -> dict[str, object]:
        return {
            "results": {
                "ticker": "SPY",
                "active": True,
                "delisted": False,
                "primary_exchange": "XASE",
                "type": "ETF",
                "name": "SPDR S&P 500 ETF Trust",
                "currency": "USD",
            }
        }

    def _qqq_payload(self) -> dict[str, object]:
        return {
            "results": [
                {
                    "ticker": "QQQ",
                    "active": True,
                    "delisted": False,
                    "primary_exchange": "XNAS",
                    "type": "ETF",
                    "name": "Invesco QQQ Trust",
                    "currency": "USD",
                }
            ]
        }

    def test_specific_symbol_input(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.fetch_reference_ticker_payload.return_value = self._spy_payload()
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "_build_adapter", return_value=adapter
        ), patch("builtins.print") as print_mock, patch("sys.argv", ["fetch_polygon_symbol_master_by_symbols.py", "--live-check", "--symbol", "SPY"]):
            mod.main()

        adapter.fetch_reference_ticker_payload.assert_called_once_with("SPY")
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("requested_count=1", printed)
        self.assertIn("found_count=1", printed)
        self.assertIn("missing_count=0", printed)
        self.assertIn("valid_count=1", printed)
        self.assertIn("failed_count=0", printed)

    def test_candidate_list_input(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.fetch_reference_ticker_payload.side_effect = lambda symbol: self._spy_payload() if symbol == "SPY" else self._qqq_payload()
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "_build_adapter", return_value=adapter
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["fetch_polygon_symbol_master_by_symbols.py", "--live-check", "--from-etf-index-candidates"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("requested_count=", printed)
        self.assertIn("rows_written=0", printed)

    def test_missing_api_key_behavior(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "sys.argv", ["fetch_polygon_symbol_master_by_symbols.py", "--live-check", "--symbol", "SPY"]
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_dry_run_no_writes(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.map_reference_ticker.return_value = type(
            "Record",
            (),
            {"symbol": "SPY", "active": True, "vendor": "polygon", "vendor_symbol": "SPY", "exchange": "XASE", "asset_type": "etf"},
        )()
        with patch.object(mod, "_build_adapter", return_value=adapter), patch.object(mod, "SymbolMasterWriter") as writer_cls, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["fetch_polygon_symbol_master_by_symbols.py", "--symbol", "SPY"],
        ):
            mod.main()

        writer_cls.assert_not_called()

    def test_confirm_write_writer_handoff(self) -> None:
        mod = self._module()
        from app.normalization.symbol_master import NormalizedSymbolMasterRecord

        adapter = Mock()
        adapter.fetch_reference_ticker_payload.return_value = self._spy_payload()
        adapter.map_reference_ticker.return_value = NormalizedSymbolMasterRecord(
            symbol="SPY",
            active=True,
            vendor="polygon",
            vendor_symbol="SPY",
            exchange="XASE",
            asset_type="etf",
            name="SPDR S&P 500 ETF Trust",
            currency="USD",
        )
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "skipped_count": 0, "succeeded": True})()
        connection = Mock()
        with patch.dict(
            os.environ,
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://example"},
            clear=True,
        ), patch.object(mod, "_build_adapter", return_value=adapter), patch.object(mod, "_open_connection", return_value=connection), patch.object(
            mod, "SymbolMasterWriter", return_value=writer
        ) as writer_cls, patch("builtins.print"), patch(
            "sys.argv",
            ["fetch_polygon_symbol_master_by_symbols.py", "--live-check", "--confirm-write", "--symbol", "SPY"],
        ):
            mod.main()

        writer_cls.assert_called_once_with(connection)
        writer.write.assert_called_once()

    def test_rate_limit_stops_safely(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.fetch_reference_ticker_payload.side_effect = [RuntimeError("429 rate limit"), self._qqq_payload()]
        adapter.map_reference_ticker.return_value = type(
            "Record",
            (),
            {"symbol": "QQQ", "active": True, "vendor": "polygon", "vendor_symbol": "QQQ", "exchange": "XNAS", "asset_type": "etf"},
        )()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "_build_adapter", return_value=adapter
        ), patch("builtins.print") as print_mock, patch("sys.argv", ["fetch_polygon_symbol_master_by_symbols.py", "--live-check", "--symbol", "SPY", "--symbol", "QQQ"]):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("rate_limit_detected=True", printed)
        self.assertIn("found_count=0", printed)
        self.assertIn("failed_count=0", printed)

    def test_sleep_option_used_without_slowing_tests(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.fetch_reference_ticker_payload.return_value = self._spy_payload()
        adapter.map_reference_ticker.return_value = type(
            "Record",
            (),
            {"symbol": "SPY", "active": True, "vendor": "polygon", "vendor_symbol": "SPY", "exchange": "XASE", "asset_type": "etf"},
        )()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "_build_adapter", return_value=adapter
        ), patch.object(mod.time, "sleep") as sleep_mock, patch("builtins.print"), patch(
            "sys.argv",
            ["fetch_polygon_symbol_master_by_symbols.py", "--live-check", "--sleep-seconds-between-symbols", "2", "--symbol", "SPY", "--symbol", "QQQ"],
        ):
            mod.main()

        sleep_mock.assert_called_once_with(2.0)

    def test_confirm_write_only_writes_successfully_fetched_valid_records(self) -> None:
        mod = self._module()
        from app.normalization.symbol_master import NormalizedSymbolMasterRecord

        adapter = Mock()
        adapter.fetch_reference_ticker_payload.side_effect = [self._spy_payload(), RuntimeError("429 rate limit")]
        adapter.map_reference_ticker.return_value = NormalizedSymbolMasterRecord(
            symbol="SPY",
            active=True,
            vendor="polygon",
            vendor_symbol="SPY",
            exchange="XASE",
            asset_type="etf",
            name="SPDR S&P 500 ETF Trust",
            currency="USD",
        )
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "skipped_count": 0, "succeeded": True})()
        connection = Mock()
        with patch.dict(
            os.environ,
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://example"},
            clear=True,
        ), patch.object(mod, "_build_adapter", return_value=adapter), patch.object(mod, "_open_connection", return_value=connection), patch.object(
            mod, "SymbolMasterWriter", return_value=writer
        ), patch("builtins.print"), patch(
            "sys.argv",
            ["fetch_polygon_symbol_master_by_symbols.py", "--live-check", "--confirm-write", "--symbol", "SPY", "--symbol", "QQQ"],
        ):
            mod.main()

        written_records = writer.write.call_args.args[0]
        self.assertEqual(len(written_records), 1)
        self.assertEqual(written_records[0].symbol, "SPY")

    def test_missing_symbol_reported_safely(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.fetch_reference_ticker_payload.return_value = {}
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "_build_adapter", return_value=adapter
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["fetch_polygon_symbol_master_by_symbols.py", "--live-check", "--symbol", "SPY"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("found_count=0", printed)
        self.assertIn("missing_count=1", printed)
        self.assertIn("failed_count=1", printed)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/fetch_polygon_symbol_master_by_symbols.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("ai_market_machine_data", text)
        self.assertNotIn("import requests", text.lower())
        self.assertNotIn("import httpx", text.lower())
        self.assertIn("SymbolMasterWriter", text)

    def test_docs_cover_targeted_lookup(self) -> None:
        text = Path("docs/polygon_symbol_master_targeted_lookup.md").read_text(encoding="utf-8").lower()
        self.assertIn("targeted lookup", text)
        self.assertIn("from-etf-index-candidates", text)
        self.assertIn("free-tier", text)
        self.assertIn("confirm-write", text)
        self.assertIn("symbolmasterwriter", text)
