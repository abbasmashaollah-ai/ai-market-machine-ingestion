from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class FlowsPositioningFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_flows_positioning as mod

        return mod

    def test_fixture_generation(self) -> None:
        from app.normalization.flows_positioning import DEFAULT_FIXTURE_RECORDS

        self.assertEqual(len(DEFAULT_FIXTURE_RECORDS), 6)
        record_types = [record["record_type"] for record in DEFAULT_FIXTURE_RECORDS]
        self.assertEqual(
            record_types,
            [
                "ETF flows",
                "fund flows",
                "short interest",
                "institutional positioning",
                "CFTC/COT positioning",
                "dark pool/off-exchange volume",
            ],
        )

    def test_normalized_field_alignment(self) -> None:
        from app.normalization.flows_positioning import normalize_flows_positioning_record

        record = normalize_flows_positioning_record(
            {
                "record_id": "flows-2026-05-29-etf",
                "record_type": "ETF flows",
                "observation_date": "2026-05-29",
                "symbol": "SPY",
                "asset_class": "equity",
                "value": 125000000.0,
                "unit": "usd",
                "source": "manual_fixture",
                "raw_source_id": "fixture-etf-flows-1",
                "notes": "deterministic fixture",
            }
        )
        self.assertEqual(record.record_id, "flows-2026-05-29-etf")
        self.assertEqual(record.record_type, "ETF flows")
        self.assertEqual(record.observation_date, "2026-05-29")
        self.assertEqual(record.symbol, "SPY")
        self.assertEqual(record.asset_class, "equity")
        self.assertEqual(record.value, 125000000.0)
        self.assertEqual(record.unit, "usd")
        self.assertEqual(record.source, "manual_fixture")
        self.assertEqual(record.raw_source_id, "fixture-etf-flows-1")
        self.assertEqual(record.notes, "deterministic fixture")

    def test_dry_run_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=6", printed)
        self.assertIn("normalized_count=6", printed)
        self.assertIn("valid_count=6", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("record_types=['CFTC/COT positioning', 'ETF flows', 'dark pool/off-exchange volume', 'fund flows', 'institutional positioning', 'short interest']", printed)
        self.assertIn("symbols=['AAPL', 'MSFT', 'QQQ', 'SPY', 'VTI']", printed)
        self.assertIn("asset_classes=['equity', 'futures']", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_reads=True", printed)
        self.assertIn("no_db_writes=True", printed)

    def test_record_type_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--record-type", "ETF flows"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("record_types=['ETF flows']", printed)

    def test_symbol_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--symbol", "SPY"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("symbols=['SPY']", printed)

    def test_asset_class_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--asset-class", "futures"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("asset_classes=['futures']", printed)

    def test_show_records_and_invalid(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-records", "--show-invalid"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("records=(", printed)
        self.assertIn("invalid_records=(", printed)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_flows_positioning.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/flows_positioning_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("flows/positioning foundation", text)
        self.assertIn("record_id", text)
        self.assertIn("record_type", text)
        self.assertIn("observation_date", text)
        self.assertIn("asset_class", text)
        self.assertIn("raw_source_id", text)
        self.assertIn("no vendor calls", text)
        self.assertIn("no db writes", text)
        manual_doc = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("scripts.dry_run_flows_positioning", manual_doc)
