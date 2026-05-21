import os
import sys
import unittest
from dataclasses import dataclass
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

from app.vendors.common.http import HttpResponse, ResponseMetadata

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probe_fred_catalog.py"
SPEC = util.spec_from_file_location("probe_fred_catalog", MODULE_PATH)
probe_module = util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = probe_module
SPEC.loader.exec_module(probe_module)


@dataclass(frozen=True)
class FakeResult:
    summary: object
    payload: object
    response: HttpResponse
    request_metadata: object


class FredCatalogProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_priority_one_default_selection(self) -> None:
        selected = probe_module.select_catalog_series()
        self.assertTrue(all(series.priority == 1 for series in selected))
        self.assertGreater(len(selected), 0)

    def test_all_behavior(self) -> None:
        default_selected = probe_module.select_catalog_series()
        all_selected = probe_module.select_catalog_series(include_all=True)
        self.assertGreaterEqual(len(all_selected), len(default_selected))

    def test_category_filtering(self) -> None:
        selected = probe_module.select_catalog_series(category="inflation")
        self.assertTrue(all(series.category.value == "inflation" for series in selected))

    def test_safe_output_redacts_api_key(self) -> None:
        result = FakeResult(
            summary=probe_module.CatalogProbeSummary(
                series_id="GDP",
                category="economic_growth",
                row_count=0,
                first_date=None,
                last_date=None,
                status_code=200,
            ),
            payload={"error_message": "rate limit reached"},
            response=HttpResponse(
                metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
                text='{"error_message": "rate limit reached"}',
                json={"error_message": "rate limit reached", "observations": []},
            ),
            request_metadata=Mock(query_params={"api_key": "secret", "file_type": "json"}),
        )
        line = probe_module.format_debug_safe_line(result, result.summary)
        self.assertNotIn("secret", line)
        self.assertIn("file_type", line)
        self.assertIn("json", line)

    def test_mocked_successful_summary(self) -> None:
        fake_result = FakeResult(
            summary=probe_module.CatalogProbeSummary(
                series_id="GDP",
                category="economic_growth",
                row_count=1,
                first_date="2026-01-01",
                last_date="2026-01-01",
                status_code=200,
            ),
            payload={"observations": [{"date": "2026-01-01"}]},
            response=HttpResponse(
                metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
                text='{"observations": [{"date": "2026-01-01"}]}',
                json={"observations": [{"date": "2026-01-01"}]},
            ),
            request_metadata=Mock(query_params={"api_key": "secret", "file_type": "json"}),
        )
        summaries = probe_module.summarize_catalog_results([fake_result])
        self.assertEqual(summaries[0].series_id, "GDP")
        self.assertEqual(summaries[0].status_code, 200)

    def test_no_live_api_calls_in_tests(self) -> None:
        with patch.object(probe_module, "run_probe_details", return_value=[]):
            self.assertEqual(probe_module.select_catalog_series(include_all=False)[0].priority, 1)
