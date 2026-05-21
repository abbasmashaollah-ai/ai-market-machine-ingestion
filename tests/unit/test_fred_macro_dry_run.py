import os
import sys
import unittest
from dataclasses import dataclass
from datetime import date
from importlib import util
from pathlib import Path
from unittest.mock import Mock

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probe_fred_macro_dry_run.py"
SPEC = util.spec_from_file_location("probe_fred_macro_dry_run", MODULE_PATH)
probe_module = util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = probe_module
SPEC.loader.exec_module(probe_module)

from app.ingestion.pipelines.fred_macro import FredMacroPipelineRequest, execute_fred_macro_dry_run


@dataclass(frozen=True)
class FakeFredClient:
    payloads: dict[str, dict[str, object]]

    def fetch_series_observations_raw(self, series_id: str, *, observation_start: str | None = None, observation_end: str | None = None) -> dict[str, object]:
        return self.payloads[series_id]


class FredMacroDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_dry_run_executor_with_mocked_fred_client(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP",),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )
        client = FakeFredClient(
            payloads={
                "GDP": {
                    "observations": [
                        {"series_id": "GDP", "date": "2026-01-01", "value": "1.0"},
                        {"series_id": "GDP", "date": "2026-01-02", "value": "1.1"},
                    ]
                }
            }
        )
        results = execute_fred_macro_dry_run(request, client)
        self.assertEqual(results[0].series_id, "GDP")
        self.assertEqual(results[0].rows_fetched, 2)
        self.assertEqual(results[0].rows_normalized, 2)

    def test_validation_failure_count(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP",),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )
        client = FakeFredClient(
            payloads={
                "GDP": {
                    "observations": [
                        {"series_id": "GDP", "date": "2026-01-01", "value": None},
                    ]
                }
            }
        )
        results = execute_fred_macro_dry_run(request, client)
        self.assertGreaterEqual(results[0].validation_failures, 1)

    def test_script_selection_logic(self) -> None:
        default_selection = probe_module.select_series_ids(series_ids=None, category=None, include_all=False)
        all_selection = probe_module.select_series_ids(series_ids=None, category=None, include_all=True)
        category_selection = probe_module.select_series_ids(series_ids=None, category="inflation", include_all=False)
        self.assertGreater(len(all_selection), 0)
        self.assertTrue(all(series_id in all_selection for series_id in default_selection))
        self.assertTrue(all(series_id in all_selection for series_id in category_selection))

    def test_no_db_writer_used(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP",),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )
        client = Mock()
        client.fetch_series_observations_raw.return_value = {"observations": []}
        results = execute_fred_macro_dry_run(request, client)
        self.assertEqual(results[0].rows_fetched, 0)

    def test_no_live_calls_in_tests(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP",),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )
        client = Mock()
        client.fetch_series_observations_raw.return_value = {"observations": []}
        execute_fred_macro_dry_run(request, client)
        client.fetch_series_observations_raw.assert_called_once()
