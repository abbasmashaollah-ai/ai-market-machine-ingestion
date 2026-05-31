from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class OptionsFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_options as mod

        return mod

    def test_fixture_generation(self) -> None:
        from app.normalization.options import DEFAULT_FIXTURE_RECORDS

        self.assertEqual(len(DEFAULT_FIXTURE_RECORDS), 4)
        contracts = [record["contract_symbol"] for record in DEFAULT_FIXTURE_RECORDS]
        self.assertEqual(
            contracts,
            [
                "AAPL260619C00250000",
                "AAPL260619P00250000",
                "SPY260619C00550000",
                "SPY260619P00550000",
            ],
        )

    def test_normalized_field_alignment(self) -> None:
        from app.normalization.options import normalize_options_record

        record = normalize_options_record(
            {
                "contract_symbol": "AAPL260619C00250000",
                "underlying_symbol": "AAPL",
                "expiration_date": "2026-06-19",
                "strike": 250.0,
                "option_type": "call",
                "bid": 11.2,
                "ask": 11.4,
                "last": 11.3,
                "volume": 15420,
                "open_interest": 84210,
                "implied_volatility": 0.24,
                "source": "manual_fixture",
                "notes": "deterministic fixture",
            }
        )
        self.assertEqual(record.contract_symbol, "AAPL260619C00250000")
        self.assertEqual(record.underlying_symbol, "AAPL")
        self.assertEqual(record.expiration_date, "2026-06-19")
        self.assertEqual(record.strike, 250.0)
        self.assertEqual(record.option_type, "call")
        self.assertEqual(record.bid, 11.2)
        self.assertEqual(record.ask, 11.4)
        self.assertEqual(record.last, 11.3)
        self.assertEqual(record.volume, 15420.0)
        self.assertEqual(record.open_interest, 84210.0)
        self.assertEqual(record.implied_volatility, 0.24)
        self.assertEqual(record.source, "manual_fixture")
        self.assertEqual(record.notes, "deterministic fixture")

    def test_dry_run_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=4", printed)
        self.assertIn("normalized_count=4", printed)
        self.assertIn("valid_count=4", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("underlying_symbols=['AAPL', 'SPY']", printed)
        self.assertIn("option_types=['call', 'put']", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_reads=True", printed)
        self.assertIn("no_db_writes=True", printed)

    def test_underlying_symbol_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--underlying-symbol", "AAPL"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=2", printed)
        self.assertIn("underlying_symbols=['AAPL']", printed)

    def test_option_type_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--option-type", "put"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=2", printed)
        self.assertIn("option_types=['put']", printed)

    def test_show_records_and_invalid(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-records", "--show-invalid"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("records=(", printed)
        self.assertIn("invalid_records=(", printed)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_options.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/options_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("options foundation", text)
        self.assertIn("contract_symbol", text)
        self.assertIn("underlying_symbol", text)
        self.assertIn("expiration_date", text)
        self.assertIn("implied_volatility", text)
        self.assertIn("no vendor calls", text)
        self.assertIn("no db writes", text)
        manual_doc = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("scripts.dry_run_options", manual_doc)
