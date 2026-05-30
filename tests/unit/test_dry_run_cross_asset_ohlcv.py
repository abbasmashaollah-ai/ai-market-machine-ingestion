from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class CrossAssetOhlcvFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_cross_asset_ohlcv as mod

        return mod

    def test_fixture_generation(self) -> None:
        from app.normalization.cross_asset_ohlcv import DEFAULT_FIXTURE_RECORDS

        self.assertEqual(len(DEFAULT_FIXTURE_RECORDS), 5)
        groups = [record["asset_group"] for record in DEFAULT_FIXTURE_RECORDS]
        self.assertEqual(
            groups,
            [
                "bonds/rates proxy",
                "DXY / dollar index proxy",
                "commodity proxy",
                "crypto proxy",
                "FX proxy",
            ],
        )

    def test_normalized_field_alignment(self) -> None:
        from app.normalization.cross_asset_ohlcv import normalize_cross_asset_ohlcv_record

        record = normalize_cross_asset_ohlcv_record(
            {
                "symbol": "TLT",
                "asset_group": "bonds/rates proxy",
                "market_date": "2026-05-29",
                "open": 92.1,
                "high": 92.8,
                "low": 91.9,
                "close": 92.4,
                "volume": 1234567,
                "source": "manual_fixture",
                "vendor_symbol": "TLT",
                "notes": "deterministic fixture",
            }
        )
        self.assertEqual(record.symbol, "TLT")
        self.assertEqual(record.asset_group, "bonds/rates proxy")
        self.assertEqual(record.market_date, "2026-05-29")
        self.assertEqual(record.open, 92.1)
        self.assertEqual(record.high, 92.8)
        self.assertEqual(record.low, 91.9)
        self.assertEqual(record.close, 92.4)
        self.assertEqual(record.volume, 1234567.0)
        self.assertEqual(record.source, "manual_fixture")
        self.assertEqual(record.vendor_symbol, "TLT")
        self.assertEqual(record.notes, "deterministic fixture")

    def test_dry_run_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=5", printed)
        self.assertIn("normalized_count=5", printed)
        self.assertIn("valid_count=5", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("asset_groups=['DXY / dollar index proxy', 'FX proxy', 'bonds/rates proxy', 'commodity proxy', 'crypto proxy']", printed)
        self.assertIn("symbols=['BTC-USD', 'EURUSD', 'GLD', 'TLT', 'UUP']", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_reads=True", printed)
        self.assertIn("no_db_writes=True", printed)

    def test_symbol_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--symbol", "TLT"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("symbols=['TLT']", printed)

    def test_asset_group_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--asset-group", "crypto proxy"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("asset_groups=['crypto proxy']", printed)

    def test_show_records_and_invalid(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-records", "--show-invalid"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("records=(", printed)
        self.assertIn("invalid_records=(", printed)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_cross_asset_ohlcv.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/cross_asset_ohlcv_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("cross-asset ohlcv foundation", text)
        self.assertIn("symbol", text)
        self.assertIn("asset_group", text)
        self.assertIn("market_date", text)
        self.assertIn("vendor_symbol", text)
        self.assertIn("no vendor calls", text)
        self.assertIn("no db writes", text)
        manual_doc = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("scripts.dry_run_cross_asset_ohlcv", manual_doc)
