import unittest
from unittest.mock import Mock

from app.vendors.common.http import HttpResponse, ResponseMetadata
from app.vendors.fred.client import FredClientConfig, UnsupportedFredClient


class FredClientTransportTests(unittest.TestCase):
    def test_observations_request_uses_expected_path_and_params(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"observations": [{"series_id": "CPIAUCSL"}]}',
            json={"observations": [{"series_id": "CPIAUCSL"}]},
        )
        client = UnsupportedFredClient(FredClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_series_observations_raw("CPIAUCSL")

        metadata = transport.request.call_args[0][0]
        self.assertIn("/fred/series/observations?series_id=CPIAUCSL", metadata.url)
        self.assertEqual(metadata.query_params["api_key"], "secret")
        self.assertEqual(metadata.query_params["file_type"], "json")
        self.assertEqual(result, {"observations": [{"series_id": "CPIAUCSL"}]})

    def test_metadata_request_uses_expected_path_and_params(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"id": "CPIAUCSL"}',
            json={"id": "CPIAUCSL"},
        )
        client = UnsupportedFredClient(FredClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_series_metadata_raw("CPIAUCSL")

        metadata = transport.request.call_args[0][0]
        self.assertIn("/fred/series?series_id=CPIAUCSL", metadata.url)
        self.assertEqual(metadata.query_params["api_key"], "secret")
        self.assertEqual(metadata.query_params["file_type"], "json")
        self.assertEqual(result, {"id": "CPIAUCSL"})

    def test_api_key_passed_via_params_not_logged(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text="{}",
            json={},
        )
        client = UnsupportedFredClient(FredClientConfig(api_key="secret"), http_client=transport)

        client.fetch_series_metadata_raw("CPIAUCSL")

        metadata = transport.request.call_args[0][0]
        self.assertEqual(metadata.query_params["api_key"], "secret")
        self.assertEqual(metadata.query_params["file_type"], "json")
        self.assertNotIn("secret", metadata.url)

    def test_client_returns_raw_payload(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"observations": [{"series_id": "CPIAUCSL"}]}',
            json={"observations": [{"series_id": "CPIAUCSL"}]},
        )
        client = UnsupportedFredClient(FredClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_series_observations_raw("CPIAUCSL")

        self.assertEqual(result, {"observations": [{"series_id": "CPIAUCSL"}]})

    def test_no_live_http_calls(self) -> None:
        client = UnsupportedFredClient(FredClientConfig(api_key="secret"))
        with self.assertRaises(NotImplementedError):
            client.fetch_series_observations_raw("CPIAUCSL")
