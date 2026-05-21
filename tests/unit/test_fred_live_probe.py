import os
import sys
import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probe_fred_series.py"
SPEC = util.spec_from_file_location("probe_fred_series", MODULE_PATH)
probe_module = util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = probe_module
SPEC.loader.exec_module(probe_module)

ProbeSummary = probe_module.ProbeSummary
ProbeResult = probe_module.ProbeResult
run_probe = probe_module.run_probe
run_probe_details = probe_module.run_probe_details
summarize_observations = probe_module.summarize_observations
extract_safe_debug_details = probe_module.extract_safe_debug_details


class FredLiveProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_missing_api_key_behavior(self) -> None:
        os.environ.pop("FRED_API_KEY", None)
        with patch.object(probe_module, "load_local_env_if_available", return_value=False):
            with self.assertRaises(RuntimeError):
                run_probe(client=Mock())

    def test_optional_dotenv_loading(self) -> None:
        fake_dotenv = Mock()
        fake_dotenv.load_dotenv.return_value = True
        with patch.dict(sys.modules, {"dotenv": fake_dotenv}):
            self.assertTrue(probe_module.load_local_env_if_available())

    def test_safe_output_does_not_include_api_key(self) -> None:
        summary = summarize_observations("GDP", [{"date": "2026-01-01"}])
        self.assertEqual(summary.series_id, "GDP")
        self.assertNotIn("api_key", summary.__dict__)

    def test_mocked_successful_probe_summary(self) -> None:
        os.environ["FRED_API_KEY"] = "secret"
        client = Mock()
        client.fetch_series_observations_raw.return_value = {
            "observations": [{"date": "2026-01-01"}, {"date": "2026-01-02"}]
        }

        summaries = run_probe(series_ids=("GDP",), observation_start="2026-01-01", observation_end="2026-01-02", client=client)

        self.assertEqual(summaries, [ProbeSummary(series_id="GDP", row_count=2, first_date="2026-01-01", last_date="2026-01-02")])
        called_args = client.fetch_series_observations_raw.call_args[1]
        self.assertEqual(called_args["observation_start"], "2026-01-01")
        self.assertEqual(called_args["observation_end"], "2026-01-02")

    def test_extracts_observations_key_payload(self) -> None:
        rows = probe_module.extract_observation_rows({"observations": [{"date": "2026-01-01"}]})
        self.assertEqual(rows, [{"date": "2026-01-01"}])

    def test_debug_safe_details_are_secret_free(self) -> None:
        details = extract_safe_debug_details({"observations": [], "error_message": "rate limit reached"})
        self.assertEqual(details["response_keys"], ["error_message", "observations"])
        self.assertEqual(details["fred_error"], "rate limit reached")

    def test_no_live_api_calls_during_tests(self) -> None:
        os.environ["FRED_API_KEY"] = "secret"
        client = Mock()
        client.fetch_series_observations_raw.return_value = []
        run_probe(series_ids=("GDP",), client=client)
        client.fetch_series_observations_raw.assert_called_once()

    def test_run_probe_details_with_mocked_payload(self) -> None:
        os.environ["FRED_API_KEY"] = "secret"
        client = Mock()
        client.fetch_series_observations_raw.return_value = {
            "observations": [{"date": "2026-01-01"}],
            "notes": "ok",
        }

        results = run_probe_details(series_ids=("GDP",), observation_start="2026-01-01", observation_end="2026-01-02", client=client)

        self.assertEqual(results, [ProbeResult(summary=ProbeSummary(series_id="GDP", row_count=1, first_date="2026-01-01", last_date="2026-01-01"), payload={"observations": [{"date": "2026-01-01"}], "notes": "ok"})])
