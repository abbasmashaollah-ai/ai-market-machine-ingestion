import os
import sys
import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

from app.vendors.common.http import HttpResponse, ResponseMetadata

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
build_series_request_metadata = probe_module.build_series_request_metadata


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
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"observations": [{"date": "2026-01-01"}, {"date": "2026-01-02"}]}',
            json={"observations": [{"date": "2026-01-01"}, {"date": "2026-01-02"}]},
        )
        client = Mock()
        client.http_client = transport
        client.config = Mock(base_url="https://api.stlouisfed.org", timeout_seconds=30.0)

        summaries = run_probe(series_ids=("GDP",), observation_start="2026-01-01", observation_end="2026-01-02", client=client)

        self.assertEqual(summaries, [ProbeSummary(series_id="GDP", row_count=2, first_date="2026-01-01", last_date="2026-01-02")])
        called_args = transport.request.call_args[0][0]
        self.assertEqual(called_args.query_params["observation_start"], "2026-01-01")
        self.assertEqual(called_args.query_params["observation_end"], "2026-01-02")

    def test_extracts_observations_key_payload(self) -> None:
        rows = probe_module.extract_observation_rows({"observations": [{"date": "2026-01-01"}]})
        self.assertEqual(rows, [{"date": "2026-01-01"}])

    def test_debug_safe_details_are_secret_free(self) -> None:
        details = extract_safe_debug_details({"observations": [], "error_message": "rate limit reached"})
        self.assertEqual(details["response_keys"], ["error_message", "observations"])
        self.assertEqual(details["fred_error"], "rate limit reached")

    def test_build_series_request_metadata_redacts_api_key(self) -> None:
        metadata = build_series_request_metadata(
            base_url="https://api.stlouisfed.org",
            api_key="secret",
            series_id="GDP",
            observation_start="2026-01-01",
            observation_end="2026-01-02",
            timeout_seconds=30.0,
        )
        self.assertEqual(metadata.query_params["api_key"], "secret")
        self.assertNotIn("secret", metadata.url)

    def test_empty_response_text_is_reported(self) -> None:
        response = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text="",
            json=None,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.raw_text_length, 0)
        self.assertIsNone(response.parsed_json)

    def test_non_200_response_is_reported(self) -> None:
        response = HttpResponse(
            metadata=ResponseMetadata(status_code=503, elapsed_seconds=0.1),
            text='{"error_message": "service unavailable"}',
            json={"error_message": "service unavailable"},
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.raw_text_length, len('{"error_message": "service unavailable"}'))
        self.assertEqual(response.parsed_json["error_message"], "service unavailable")

    def test_no_live_api_calls_during_tests(self) -> None:
        os.environ["FRED_API_KEY"] = "secret"
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text="{}",
            json={},
        )
        client = Mock()
        client.http_client = transport
        client.config = Mock(base_url="https://api.stlouisfed.org", timeout_seconds=30.0)
        run_probe(series_ids=("GDP",), client=client)
        transport.request.assert_called_once()

    def test_run_probe_details_with_mocked_payload(self) -> None:
        os.environ["FRED_API_KEY"] = "secret"
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"observations": [{"date": "2026-01-01"}], "notes": "ok"}',
            json={"observations": [{"date": "2026-01-01"}], "notes": "ok"},
        )
        client = Mock()
        client.http_client = transport
        client.config = Mock(base_url="https://api.stlouisfed.org", timeout_seconds=30.0)

        results = run_probe_details(series_ids=("GDP",), observation_start="2026-01-01", observation_end="2026-01-02", client=client)

        self.assertEqual(results[0].summary, ProbeSummary(series_id="GDP", row_count=1, first_date="2026-01-01", last_date="2026-01-01"))
        self.assertEqual(results[0].payload, {"observations": [{"date": "2026-01-01"}], "notes": "ok"})
        self.assertEqual(results[0].response.status_code, 200)
