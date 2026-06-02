from __future__ import annotations

import os
import unittest
from datetime import date
from unittest.mock import Mock, patch


class VolatilityLiveSourceDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.volatility_live_source_dry_run as mod

        return mod

    def test_refuses_live_call_without_confirmation_flag(self) -> None:
        mod = self._module()
        with patch.object(mod, "PolygonVolatilityIndexAdapter") as adapter_mock:
            with self.assertRaises(RuntimeError):
                mod.main([])
        adapter_mock.assert_not_called()

    def test_default_symbols_are_starter_symbols(self) -> None:
        mod = self._module()
        self.assertEqual(mod.DEFAULT_SYMBOLS, ("VIX", "VVIX", "VXN", "RVX"))

    def test_fake_vendor_records_are_handed_to_producer(self) -> None:
        mod = self._module()
        from app.normalization.volatility_index import NormalizedVolatilityIndexRecord

        adapter = Mock()
        adapter.fetch_symbol_records.side_effect = [
            [NormalizedVolatilityIndexRecord("VIX", date(2026, 5, 21), 18.2, "polygon", "I:VIX", "index", "latest")],
            [NormalizedVolatilityIndexRecord("VVIX", date(2026, 5, 21), 92.1, "polygon", "I:VVIX", "index", "latest")],
            [NormalizedVolatilityIndexRecord("VXN", date(2026, 5, 21), 21.7, "polygon", "I:VXN", "index", "latest")],
            [NormalizedVolatilityIndexRecord("RVX", date(2026, 5, 21), 25.4, "polygon", "I:RVX", "index", "latest")],
        ]

        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonVolatilityIndexAdapter", return_value=adapter
        ), patch("builtins.print") as print_mock:
            mod.main(["--confirm-live"])

        self.assertEqual(adapter.fetch_symbol_records.call_count, 4)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("requested_symbols=['VIX', 'VVIX', 'VXN', 'RVX']", printed)
        self.assertIn("fetched_count=4", printed)
        self.assertIn("accepted_count=4", printed)
        self.assertIn("rejected_count=0", printed)
        self.assertIn("no_db_writes=true", printed)
        self.assertNotIn("polygon-secret", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)

    def test_entitlement_errors_become_safe_warnings(self) -> None:
        mod = self._module()

        adapter = Mock()
        adapter.fetch_symbol_records.side_effect = [
            RuntimeError("HTTP 401 unauthorized for polygon api key"),
            [],
            [],
            [],
        ]
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonVolatilityIndexAdapter", return_value=adapter
        ), patch("builtins.print") as print_mock:
            mod.main(["--confirm-live"])

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("error_categories=['entitlement_failure']", printed)
        self.assertIn("warnings=['VIX: HTTP 401 unauthorized for polygon api key']", printed)
        self.assertIn("no_scheduler_activation=true", printed)

    def test_no_db_writer_is_invoked(self) -> None:
        mod = self._module()
        adapter = Mock()
        adapter.fetch_symbol_records.return_value = []
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "PolygonVolatilityIndexAdapter", return_value=adapter
        ), patch.object(mod, "build_volatility_observations_dry_run", wraps=mod.build_volatility_observations_dry_run) as producer_mock, patch(
            "builtins.print"
        ):
            mod.main(["--confirm-live"])

        producer_mock.assert_called_once()

