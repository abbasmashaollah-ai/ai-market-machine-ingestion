from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class BreadthParticipationFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_breadth_participation as mod

        return mod

    def test_fixture_generation(self) -> None:
        from app.normalization.breadth_participation import DEFAULT_FIXTURE_RECORDS

        self.assertEqual(len(DEFAULT_FIXTURE_RECORDS), 6)
        metric_types = [record["metric_type"] for record in DEFAULT_FIXTURE_RECORDS]
        self.assertEqual(
            metric_types,
            [
                "advance_decline_count",
                "new_highs_new_lows",
                "percent_above_moving_average",
                "up_down_volume",
                "sector_participation",
                "index_universe_breadth",
            ],
        )

    def test_normalized_field_alignment(self) -> None:
        from app.normalization.breadth_participation import normalize_breadth_participation_record

        record = normalize_breadth_participation_record(
            {
                "metric_id": "breadth-2026-05-29-adv-dec",
                "metric_type": "advance_decline_count",
                "observation_date": "2026-05-29",
                "universe": "US equities",
                "symbol": None,
                "value": 1240,
                "numerator": 1240,
                "denominator": 980,
                "source": "manual_fixture",
                "notes": "deterministic fixture",
            }
        )
        self.assertEqual(record.metric_id, "breadth-2026-05-29-adv-dec")
        self.assertEqual(record.metric_type, "advance_decline_count")
        self.assertEqual(record.observation_date, "2026-05-29")
        self.assertEqual(record.universe, "US equities")
        self.assertIsNone(record.symbol)
        self.assertEqual(record.value, 1240.0)
        self.assertEqual(record.numerator, 1240.0)
        self.assertEqual(record.denominator, 980.0)
        self.assertEqual(record.source, "manual_fixture")
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
        self.assertIn("metric_types=['advance_decline_count', 'index_universe_breadth', 'new_highs_new_lows', 'percent_above_moving_average', 'sector_participation', 'up_down_volume']", printed)
        self.assertIn("universes=['Russell 3000', 'S&P 500', 'S&P 500 sectors', 'US equities']", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_reads=True", printed)
        self.assertIn("no_db_writes=True", printed)

    def test_metric_type_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--metric-type", "advance_decline_count"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("metric_types=['advance_decline_count']", printed)

    def test_universe_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--universe", "S&P 500"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("universes=['S&P 500']", printed)

    def test_show_records_and_invalid(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-records", "--show-invalid"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("records=(", printed)
        self.assertIn("invalid_records=(", printed)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_breadth_participation.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/breadth_participation_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("breadth/participation foundation", text)
        self.assertIn("metric_id", text)
        self.assertIn("metric_type", text)
        self.assertIn("observation_date", text)
        self.assertIn("universe", text)
        self.assertIn("numerator", text)
        self.assertIn("denominator", text)
        self.assertIn("no vendor calls", text)
        self.assertIn("no db writes", text)
        manual_doc = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("scripts.dry_run_breadth_participation", manual_doc)
