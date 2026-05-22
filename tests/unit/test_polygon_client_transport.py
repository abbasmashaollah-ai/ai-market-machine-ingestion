import unittest
from unittest.mock import Mock

from app.vendors.common.http import HttpResponse, ResponseMetadata
from app.vendors.polygon.client import PolygonClientConfig, UnsupportedPolygonClient, build_polygon_client


class PolygonClientTransportTests(unittest.TestCase):
    def test_aggregate_request_uses_expected_path_and_params(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"results": [{"ticker": "AAPL"}]}',
            json={"results": [{"ticker": "AAPL"}]},
        )
        client = UnsupportedPolygonClient(PolygonClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_aggregates_raw("AAPL", "2026-01-01", "2026-01-31")

        metadata = transport.request.call_args[0][0]
        self.assertIn("/v2/aggs/ticker/AAPL/range/1/day/2026-01-01/2026-01-31", metadata.url)
        self.assertEqual(metadata.query_params["apiKey"], "secret")
        self.assertEqual(result, [{"ticker": "AAPL"}])

    def test_ticker_request_uses_expected_path_and_params(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"results": [{"ticker": "AAPL"}]}',
            json={"results": [{"ticker": "AAPL"}]},
        )
        client = UnsupportedPolygonClient(PolygonClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_tickers_raw()

        metadata = transport.request.call_args[0][0]
        self.assertIn("/v3/reference/tickers", metadata.url)
        self.assertEqual(metadata.query_params["apiKey"], "secret")
        self.assertEqual(result, [{"ticker": "AAPL"}])

    def test_api_key_passed_via_params_not_logged(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text="[]",
            json=[],
        )
        client = UnsupportedPolygonClient(PolygonClientConfig(api_key="secret"), http_client=transport)

        client.fetch_tickers_raw()

        metadata = transport.request.call_args[0][0]
        self.assertEqual(metadata.query_params["apiKey"], "secret")
        self.assertNotIn("secret", metadata.url)

    def test_client_returns_raw_payload(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"results": [{"ticker": "AAPL"}]}',
            json={"results": [{"ticker": "AAPL"}]},
        )
        client = UnsupportedPolygonClient(PolygonClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_aggregates_raw("AAPL", "2026-01-01", "2026-01-31")

        self.assertEqual(result, [{"ticker": "AAPL"}])

    def test_no_live_http_calls(self) -> None:
        client = UnsupportedPolygonClient(PolygonClientConfig(api_key="secret"))
        with self.assertRaises(NotImplementedError):
            client.fetch_tickers_raw()

    def test_build_polygon_client_uses_shared_http_transport(self) -> None:
        client = build_polygon_client(PolygonClientConfig(api_key="secret"))
        self.assertIsInstance(client, UnsupportedPolygonClient)

    def test_aggregate_request_metadata_is_correct(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"results": [{"ticker": "SPY"}]}',
            json={"results": [{"ticker": "SPY"}]},
        )
        client = UnsupportedPolygonClient(PolygonClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_aggregates_raw("SPY", "2025-01-02", "2025-01-10")

        metadata = transport.request.call_args[0][0]
        self.assertIn("/v2/aggs/ticker/SPY/range/1/day/2025-01-02/2025-01-10", metadata.url)
        self.assertEqual(metadata.query_params["apiKey"], "secret")
        self.assertEqual(result, [{"ticker": "SPY"}])
