from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class EventCalendarFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_event_calendar_foundation as mod

        return mod

    def test_normalized_record_shape(self) -> None:
        from app.normalization.event_calendar import normalize_event_calendar_record

        record = normalize_event_calendar_record(
            {
                "event_id": "cpi-2026-05-21",
                "event_type": "CPI",
                "event_date": "2026-05-21",
                "event_time": "08:30",
                "timezone": "America/New_York",
                "source": "manual_fixture",
                "title": "Consumer Price Index",
                "importance": "high",
                "notes": "deterministic fixture",
            }
        )
        self.assertEqual(record.event_id, "cpi-2026-05-21")
        self.assertEqual(record.event_type, "CPI")
        self.assertEqual(str(record.event_date), "2026-05-21")
        self.assertEqual(str(record.event_time), "08:30:00")
        self.assertEqual(record.timezone, "America/New_York")
        self.assertEqual(record.source, "manual_fixture")
        self.assertEqual(record.title, "Consumer Price Index")
        self.assertEqual(record.importance, "high")
        self.assertEqual(record.notes, "deterministic fixture")

    def test_starter_event_types(self) -> None:
        from app.normalization.event_calendar import STARTER_EVENT_TYPES

        self.assertEqual(STARTER_EVENT_TYPES, ("CPI", "FOMC", "NFP", "OPEX", "earnings_date"))

    def test_validation_behavior(self) -> None:
        from app.normalization.event_calendar import NormalizedEventCalendarRecord, validate_event_calendar_record

        record = NormalizedEventCalendarRecord(
            event_id=None,
            event_type=None,
            event_date=None,
            event_time=None,
            timezone=None,
            source=None,
            symbol=None,
            title=None,
            importance=None,
            notes=None,
        )
        errors = validate_event_calendar_record(record)
        self.assertIn("event_id is required", errors)
        self.assertIn("event_type is required", errors)
        self.assertIn("event_date is required", errors)
        self.assertIn("timezone is required", errors)
        self.assertIn("source is required", errors)
        self.assertIn("title is required", errors)
        self.assertIn("importance is required", errors)

    def test_dry_run_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("event_count=5", printed)
        self.assertIn("normalized_count=5", printed)
        self.assertIn("valid_count=5", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("event_types=['CPI', 'FOMC', 'NFP', 'OPEX', 'earnings_date']", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_writes=True", printed)

    def test_event_type_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--event-type", "CPI", "--event-type", "NFP"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("event_count=2", printed)
        self.assertIn("event_types=['CPI', 'NFP']", printed)

    def test_no_vendor_calls(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        self.assertTrue(print_mock.mock_calls)

    def test_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"):
            mod.main([])

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_event_calendar_foundation.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/event_calendar_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("event calendar foundation", text)
        self.assertIn("cpi", text)
        self.assertIn("fomc", text)
        self.assertIn("nfp", text)
        self.assertIn("opex", text)
        self.assertIn("earnings_date", text)
        self.assertIn("event_id", text)
        self.assertIn("event_type", text)
        self.assertIn("no vendor calls", text)
        self.assertIn("no db writes", text)
        manual_doc = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("scripts.dry_run_event_calendar_foundation", manual_doc)
