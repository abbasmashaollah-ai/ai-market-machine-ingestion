from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class PolygonSymbolMasterDryRunTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_polygon_symbol_master as mod

        return mod

    def test_default_dry_run_no_vendor_or_db_calls(self) -> None:
        mod = self._module()
        with patch.object(mod, "_build_records", wraps=mod._build_records) as build_records_mock, patch.object(
            mod, "SymbolMasterWriter"
        ) as writer_cls, patch("builtins.print") as print_mock, patch("sys.argv", ["dry_run_polygon_symbol_master.py"]):
            mod.main()

        build_records_mock.assert_called_once_with(live_check=False)
        writer_cls.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("vendor=polygon", printed)
        self.assertIn("dry_run=True", printed)
        self.assertIn("rows_written=0", printed)
        self.assertIn("rows_skipped=0", printed)
        self.assertIn("write_confirmed=False", printed)

    def test_record_flags_require_database_url(self) -> None:
        mod = self._module()
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch(
            "sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check", "--record-run"]
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_recording_requires_live_check_and_confirm_write(self) -> None:
        mod = self._module()
        with patch.dict(
            "os.environ",
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://example"},
            clear=True,
        ), patch("sys.argv", ["dry_run_polygon_symbol_master.py", "--record-run"]):
            with self.assertRaisesRegex(RuntimeError, "requires --live-check and --confirm-write"):
                mod.main()

    def test_live_check_requires_polygon_key(self) -> None:
        mod = self._module()
        with patch.dict("os.environ", {}, clear=True), patch("sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check"]):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_confirm_write_requires_database_url(self) -> None:
        mod = self._module()
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch(
            "sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check", "--confirm-write"]
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_confirm_write_without_live_check_is_blocked(self) -> None:
        mod = self._module()
        with patch.dict("os.environ", {"DATABASE_URL": "postgresql://example"}, clear=True), patch(
            "sys.argv", ["dry_run_polygon_symbol_master.py", "--confirm-write"]
        ):
            with self.assertRaisesRegex(RuntimeError, "require --live-check"):
                mod.main()

    def test_live_check_and_confirm_write_calls_writer_with_normalized_records(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.fetch_reference_tickers_raw.return_value = [
            {"ticker": "AAPL", "active": True, "delisted": False, "primary_exchange": "XNAS", "type": "CS", "currency": "USD"}
        ]
        from app.normalization.symbol_master import NormalizedSymbolMasterRecord

        normalized_record = NormalizedSymbolMasterRecord(
            symbol="AAPL",
            active=True,
            vendor="polygon",
            vendor_symbol="AAPL",
        )
        adapter.map_reference_ticker.return_value = normalized_record
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "skipped_count": 0, "succeeded": True})()
        connection = Mock()
        with patch.dict(
            "os.environ",
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://example"},
            clear=True,
        ), patch.object(mod, "_build_adapter", return_value=adapter), patch.object(
            mod, "_open_connection", return_value=connection
        ), patch.object(
            mod, "SymbolMasterWriter", return_value=writer
        ) as writer_cls, patch("builtins.print") as print_mock, patch(
            "sys.argv", ["dry_run_polygon_symbol_master.py", "--live-check", "--confirm-write"]
        ):
            mod.main()

        writer_cls.assert_called_once_with(connection)
        writer.write.assert_called_once()
        written_records = writer.write.call_args.args[0]
        self.assertEqual(written_records, [normalized_record])
        self.assertIsInstance(written_records[0], NormalizedSymbolMasterRecord)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("rows_written=1", printed)
        self.assertIn("rows_skipped=0", printed)
        self.assertIn("write_confirmed=True", printed)

    def test_record_run_quality_and_lineage_call_approved_stores(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.fetch_reference_tickers_raw.return_value = [
            {"ticker": "AAPL", "active": True, "delisted": False, "primary_exchange": "XNAS", "type": "CS", "currency": "USD"}
        ]
        from app.normalization.symbol_master import NormalizedSymbolMasterRecord

        normalized_record = NormalizedSymbolMasterRecord(symbol="AAPL", active=True, vendor="polygon", vendor_symbol="AAPL")
        adapter.map_reference_ticker.return_value = normalized_record
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "skipped_count": 0, "succeeded": True})()
        run_store = Mock()
        quality_store = Mock()
        lineage_store = Mock()
        connection = Mock()
        with patch.dict(
            "os.environ",
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://example"},
            clear=True,
        ), patch.object(mod, "_build_adapter", return_value=adapter), patch.object(mod, "_open_connection", return_value=connection), patch.object(
            mod, "SymbolMasterWriter", return_value=writer
        ), patch.object(mod, "IngestionRunStore", return_value=run_store) as run_store_cls, patch.object(
            mod, "DataQualityResultStore", return_value=quality_store
        ) as quality_store_cls, patch.object(mod, "DataLineageStore", return_value=lineage_store) as lineage_store_cls, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "dry_run_polygon_symbol_master.py",
                "--live-check",
                "--confirm-write",
                "--record-run",
                "--record-quality",
                "--record-lineage",
            ],
        ):
            mod.main()

        run_store_cls.assert_called_once_with(connection)
        quality_store_cls.assert_called_once_with(connection)
        lineage_store_cls.assert_called_once_with(connection)
        self.assertTrue(run_store.save_run.called)
        self.assertTrue(quality_store.save_validation_results.called)
        self.assertTrue(lineage_store.save_chunk_lineage.called)

    def test_sanitized_vendor_errors(self) -> None:
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
        self.assertIn("SymbolMasterWriter", text)
        self.assertIn("DATABASE_URL", text)

    def test_docs_cover_command(self) -> None:
        text = Path("docs/polygon_symbol_master_dry_run.md").read_text(encoding="utf-8").lower()
        self.assertIn("polygon symbol master dry run", text)
        self.assertIn("dry_run=true", text)
        self.assertIn("live-check", text)
        self.assertIn("confirm-write", text)
        self.assertIn("symbolmasterwriter", text)
        self.assertIn("record-run", text)
        self.assertIn("record-quality", text)
        self.assertIn("record-lineage", text)
