from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch


class _Result:
    def __init__(self, rows: list[dict[str, object]] | None = None) -> None:
        self._rows = rows or []

    def fetchall(self) -> list[dict[str, object]]:
        return self._rows


class _Connection:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False

    def execute(self, sql: str, params: tuple[object, ...] = ()):
        self.executed.append((sql, params))
        return _Result(self.rows)

    def close(self) -> None:
        self.closed = True


class SymbolMasterCoverageAssessmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.assess_symbol_master_coverage as mod

        return mod

    def _rows(self) -> list[dict[str, object]]:
        return [
            {"vendor": "polygon", "exchange": "XNAS", "asset_type": "equity", "active": True, "vendor_symbol": "AAPL", "symbol": "AAPL"},
            {"vendor": "polygon", "exchange": "XNAS", "asset_type": "equity", "active": False, "vendor_symbol": None, "symbol": "MSFT"},
            {"vendor": "polygon", "exchange": None, "asset_type": "etf", "active": True, "vendor_symbol": "SPY", "symbol": "SPY"},
            {"vendor": "polygon", "exchange": "XASE", "asset_type": None, "active": True, "vendor_symbol": "QQQ", "symbol": "QQQ"},
            {"vendor": "polygon", "exchange": "XASE", "asset_type": "etf", "active": True, "vendor_symbol": "QQQ", "symbol": "QQQ"},
        ]

    def test_read_only_behavior(self) -> None:
        mod = self._module()
        connection = _Connection(self._rows())
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv", ["assess_symbol_master_coverage.py"]
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("coverage_status=FAIL", printed)
        self.assertIn("total_rows=5", printed)
        self.assertIn("active_rows=4", printed)
        self.assertIn("inactive_rows=1", printed)
        self.assertTrue(connection.closed)
        self.assertFalse(any("INSERT INTO" in sql.upper() for sql, _ in connection.executed))

    def test_filter_behavior(self) -> None:
        mod = self._module()
        connection = _Connection(self._rows())
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print"), patch(
            "sys.argv",
            ["assess_symbol_master_coverage.py", "--vendor", "polygon", "--exchange", "XNAS", "--asset-type", "equity", "--active", "true"],
        ):
            mod.main()

        sql, params = connection.executed[-1]
        self.assertIn("vendor = %s", sql)
        self.assertIn("exchange = %s", sql)
        self.assertIn("asset_type = %s", sql)
        self.assertIn("active IS TRUE", sql)
        self.assertEqual(params, ("polygon", "XNAS", "equity"))

    def test_threshold_fail_and_warn(self) -> None:
        mod = self._module()
        connection = _Connection(self._rows())
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["assess_symbol_master_coverage.py", "--min-total", "10", "--min-active", "1"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("coverage_status=FAIL", printed)

    def test_missing_metadata_ratios(self) -> None:
        mod = self._module()
        connection = _Connection(self._rows())
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["assess_symbol_master_coverage.py", "--max-missing-exchange-ratio", "0.0", "--max-missing-asset-type-ratio", "0.0"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("missing_exchange_count=1", printed)
        self.assertIn("missing_asset_type_count=1", printed)
        self.assertIn("coverage_status=FAIL", printed)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/assess_symbol_master_coverage.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("ai_market_machine_data", text)
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())

    def test_docs_cover_assessment(self) -> None:
        text = Path("docs/symbol_master_coverage_assessment.md").read_text(encoding="utf-8").lower()
        self.assertIn("coverage assessment", text)
        self.assertIn("min-total", text)
        self.assertIn("max-missing-exchange-ratio", text)
        self.assertIn("max-missing-asset-type-ratio", text)

    def test_inventory_contains_assessment_command(self) -> None:
        import scripts.verify_manual_ingestion_commands as inventory

        self.assertIn("scripts.assess_symbol_master_coverage", inventory.MODULES)
