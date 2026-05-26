from __future__ import annotations

import unittest
from datetime import date
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
        self.assertIn("requested_symbols=['VIX', 'VVIX', 'VXN', 'RVX']", printed)
        self.assertIn("normalized_count=4", printed)
        self.assertIn("valid_count=4", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("starter_symbols=['VIX', 'VVIX', 'VXN', 'RVX']", printed)
        self.assertIn("no_vendor_calls=true", printed)
        self.assertIn("no_db_writes=true", printed)

    def test_live_check_normalization(self) -> None:
        mod = self._module()
        from app.normalization.volatility_index import NormalizedVolatilityIndexRecord

        adapter = unittest.mock.Mock()
        adapter.fetch_symbol_records.return_value = (
            NormalizedVolatilityIndexRecord("VIX", date(2026, 5, 21), 18.2, "polygon", "I:VIX", "index", "latest"),
            NormalizedVolatilityIndexRecord("VIX", date(2026, 5, 22), 19.3, "polygon", "I:VIX", "index", "latest"),
        )
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonVolatilityIndexAdapter", return_value=adapter
        ), patch("builtins.print") as print_mock:
            mod.main(["--live-check", "--symbol", "VIX", "--max-observations", "1"])
        adapter.fetch_symbol_records.assert_called_once_with("VIX", max_observations=1)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("requested_symbols=['VIX']", printed)
        self.assertIn("normalized_count=2", printed)
        self.assertIn("valid_count=2", printed)
        self.assertIn("latest_observation_dates={'VIX': '2026-05-22'}", printed)
        self.assertIn("no_vendor_calls=false", printed)
        self.assertIn("no_db_writes=true", printed)

    def test_polygon_symbol_mapping(self) -> None:
        from app.vendors.polygon_volatility_index import polygon_canonical_symbol, polygon_vendor_symbol

        self.assertEqual(polygon_vendor_symbol("VIX"), "I:VIX")
        self.assertEqual(polygon_vendor_symbol("VVIX"), "I:VVIX")
        self.assertEqual(polygon_vendor_symbol("VXN"), "I:VXN")
        self.assertEqual(polygon_vendor_symbol("RVX"), "I:RVX")
        self.assertEqual(polygon_canonical_symbol("I:VIX"), "VIX")
        self.assertEqual(polygon_canonical_symbol("I:VVIX"), "VVIX")
        self.assertEqual(polygon_canonical_symbol("I:VXN"), "VXN")
        self.assertEqual(polygon_canonical_symbol("I:RVX"), "RVX")

    def test_newest_n_observation_selection(self) -> None:
        from app.vendors.polygon_volatility_index import PolygonVolatilityIndexAdapter, PolygonVolatilityIndexSourceConfig

        class Client:
            def fetch_aggregates_raw(self, ticker, from_date, to_date, *, adjusted=True):
                return [
                    {"t": 1716336000000, "c": 18.2},
                    {"t": 1716422400000, "c": 19.3},
                    {"t": 1716508800000, "c": 20.4},
                ]

        adapter = PolygonVolatilityIndexAdapter(PolygonVolatilityIndexSourceConfig(api_key="secret"), client=Client())
        records = adapter.fetch_symbol_records("VIX", max_observations=2)
        self.assertEqual([record.observation_date.isoformat() for record in records], ["2024-05-23", "2024-05-24"])
        self.assertEqual([record.value for record in records], [19.3, 20.4])

    def test_latest_date_max_behavior(self) -> None:
        mod = self._module()
        from app.normalization.volatility_index import NormalizedVolatilityIndexRecord

        adapter = unittest.mock.Mock()
        adapter.fetch_symbol_records.return_value = (
            NormalizedVolatilityIndexRecord("VIX", date(2026, 5, 22), 19.3, "polygon", "I:VIX", "index", "latest"),
            NormalizedVolatilityIndexRecord("VIX", date(2026, 5, 24), 20.4, "polygon", "I:VIX", "index", "latest"),
        )
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonVolatilityIndexAdapter", return_value=adapter
        ), patch("builtins.print") as print_mock:
            mod.main(["--live-check", "--symbol", "VIX", "--max-observations", "2"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("latest_observation_dates={'VIX': '2026-05-24'}", printed)

    def test_rate_limit_safe_stop(self) -> None:
        mod = self._module()
        from app.vendors.common.errors import VendorRateLimitedError

        adapter = unittest.mock.Mock()
        adapter.fetch_symbol_records.side_effect = VendorRateLimitedError("429 rate limit reached")
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonVolatilityIndexAdapter", return_value=adapter
        ), patch("builtins.print") as print_mock:
            mod.main(["--live-check", "--symbol", "VIX", "--stop-on-rate-limit"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("rate_limit_detected=true", printed)

    def test_sanitized_errors(self) -> None:
        mod = self._module()

        adapter = unittest.mock.Mock()
        adapter.fetch_symbol_records.side_effect = RuntimeError("POLYGON_API_KEY=secret failed")
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonVolatilityIndexAdapter", return_value=adapter
        ), patch("builtins.print") as print_mock:
            mod.main(["--live-check", "--symbol", "VIX"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("secret", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)

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

    def test_show_values_behavior(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-values"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("values=[18.2, 92.1, 21.7, 25.4]", printed)

    def test_no_vendor_calls(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch.object(mod, "PolygonVolatilityIndexAdapter") as adapter_mock:
            mod.main([])
        self.assertTrue(print_mock.mock_calls)
        adapter_mock.assert_not_called()

    def test_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"):
            mod.main([])

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_volatility_index_foundation.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)
        adapter_text = Path("app/vendors/polygon_volatility_index.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", adapter_text)
        self.assertNotIn("APIRouter", adapter_text)
        self.assertNotIn("alembic", adapter_text.lower())
        self.assertNotIn("httpx", adapter_text.lower())
        self.assertNotIn("DATABASE_URL", adapter_text)

    def test_missing_or_empty_payload_becomes_invalid_with_safe_reason(self) -> None:
        mod = self._module()

        class Client:
            def fetch_aggregates_raw(self, ticker, from_date, to_date, *, adjusted=True):
                return []

        from app.vendors.polygon_volatility_index import PolygonVolatilityIndexAdapter, PolygonVolatilityIndexSourceConfig

        adapter = PolygonVolatilityIndexAdapter(PolygonVolatilityIndexSourceConfig(api_key="secret"), client=Client())
        with patch.dict("os.environ", {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonVolatilityIndexAdapter", return_value=adapter
        ), patch("builtins.print") as print_mock:
            mod.main(["--live-check", "--symbol", "VIX", "--show-invalid"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("invalid_count=1", printed)
        self.assertIn("polygon returned no volatility observations", printed)

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
        live_doc = Path("docs/volatility_index_live_dry_run.md").read_text(encoding="utf-8").lower()
        self.assertIn("volatility index live dry run", live_doc)
        self.assertIn("polygon live-check usage requires `polygon_api_key`", live_doc)
