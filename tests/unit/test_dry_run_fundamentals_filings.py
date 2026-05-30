from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class FundamentalsFilingsFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_fundamentals_filings as mod

        return mod

    def test_fixture_generation(self) -> None:
        from app.normalization.fundamentals_filings import DEFAULT_FIXTURE_RECORDS

        self.assertEqual(len(DEFAULT_FIXTURE_RECORDS), 5)
        families = [record["record_family"] for record in DEFAULT_FIXTURE_RECORDS]
        self.assertEqual(
            families,
            [
                "company_profile",
                "financial_statement",
                "financial_metric",
                "earnings_estimate",
                "sec_filing",
            ],
        )

    def test_normalized_field_alignment(self) -> None:
        from app.normalization.fundamentals_filings import normalize_fundamentals_filings_record

        record = normalize_fundamentals_filings_record(
            {
                "record_family": "company_profile",
                "symbol": "AAPL",
                "source": "manual_fixture",
                "record_date": "2026-05-30",
                "period": "ttm",
                "payload": {"company_name": "Apple Inc."},
                "notes": "deterministic fixture",
            }
        )
        self.assertEqual(record.record_family, "company_profile")
        self.assertEqual(record.symbol, "AAPL")
        self.assertEqual(record.source, "manual_fixture")
        self.assertEqual(record.record_date, "2026-05-30")
        self.assertEqual(record.period, "ttm")
        self.assertEqual(record.payload, {"company_name": "Apple Inc."})
        self.assertEqual(record.notes, "deterministic fixture")

    def test_validation_behavior(self) -> None:
        from app.normalization.fundamentals_filings import NormalizedFundamentalsFilingsRecord, validate_fundamentals_filings_record

        record = NormalizedFundamentalsFilingsRecord(
            record_family=None,
            symbol=None,
            source=None,
            record_date=None,
            period=None,
            payload=None,
            notes=None,
        )
        errors = validate_fundamentals_filings_record(record)
        self.assertIn("record_family is required", errors)
        self.assertIn("symbol is required", errors)
        self.assertIn("source is required", errors)
        self.assertIn("record_date is required", errors)
        self.assertIn("period is required", errors)
        self.assertIn("payload is required", errors)
        self.assertIn("notes is required", errors)

    def test_dry_run_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=5", printed)
        self.assertIn("normalized_count=5", printed)
        self.assertIn("valid_count=5", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("record_families=['company_profile', 'financial_statement', 'financial_metric', 'earnings_estimate', 'sec_filing']", printed)
        self.assertIn("symbols=['AAPL', 'MSFT', 'NVDA']", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_reads=True", printed)
        self.assertIn("no_db_writes=True", printed)

    def test_symbol_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--symbol", "AAPL"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=2", printed)
        self.assertIn("symbols=['AAPL']", printed)

    def test_record_family_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--record-family", "sec_filing"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("record_families=['sec_filing']", printed)

    def test_show_records_and_invalid(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-records", "--show-invalid"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("records=(", printed)
        self.assertIn("invalid_records=(", printed)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_fundamentals_filings.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/fundamentals_filings_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("fundamentals/filings foundation", text)
        self.assertIn("company_profile", text)
        self.assertIn("financial_statement", text)
        self.assertIn("financial_metric", text)
        self.assertIn("earnings_estimate", text)
        self.assertIn("sec_filing", text)
        self.assertIn("record_family", text)
        self.assertIn("no vendor calls", text)
        self.assertIn("no db writes", text)
        manual_doc = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("scripts.dry_run_fundamentals_filings", manual_doc)
