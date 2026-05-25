import unittest
from unittest.mock import Mock

from app.vendors.common.http import HttpResponse, ResponseMetadata
from app.vendors.common.errors import VendorTimeoutError
from app.vendors.fmp.client import FmpClientConfig, FmpFetchError, FmpFetchErrorKind, UnsupportedFmpClient, build_fmp_client


class FmpClientTransportTests(unittest.TestCase):
    def test_request_uses_expected_path_and_params(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02"}]}',
            json={"historical": [{"date": "2026-01-02"}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_historical_ohlcv_raw("AAPL", start_date="2026-01-01", end_date="2026-01-31")

        metadata = transport.request.call_args[0][0]
        self.assertIn("/api/v3/historical-price-full/AAPL", metadata.url)
        self.assertEqual(metadata.query_params["from"], "2026-01-01")
        self.assertEqual(metadata.query_params["to"], "2026-01-31")
        self.assertEqual(metadata.query_params["apikey"], "secret")
        self.assertEqual(result, [{"date": "2026-01-02"}])

    def test_request_handles_list_payload(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='[{"date": "2026-01-02"}]',
            json=[{"date": "2026-01-02"}],
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)

        result = client.fetch_historical_ohlcv_raw("AAPL", start_date="2026-01-01", end_date="2026-01-31")

        self.assertEqual(result, [{"date": "2026-01-02"}])

    def test_invalid_payload_raises_classified_error(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"unexpected": true}',
            json={"unexpected": True},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)

        with self.assertRaises(FmpFetchError) as ctx:
            client.fetch_historical_ohlcv_raw("AAPL", start_date="2026-01-01", end_date="2026-01-31")

        self.assertEqual(ctx.exception.kind, FmpFetchErrorKind.INVALID_RESPONSE)
        self.assertFalse(ctx.exception.retryable)

    def test_no_live_http_calls_without_transport(self) -> None:
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"))
        with self.assertRaises(NotImplementedError):
            client.fetch_historical_ohlcv_raw("AAPL", start_date="2026-01-01", end_date="2026-01-31")

    def test_build_fmp_client_returns_supported_wrapper(self) -> None:
        client = build_fmp_client(FmpClientConfig(api_key="secret"))
        self.assertIsInstance(client, UnsupportedFmpClient)

    def test_transient_transport_error_retries_once(self) -> None:
        transport = Mock()
        transport.request.side_effect = [
            VendorTimeoutError("request timed out"),
            HttpResponse(
                metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
                text='{"historical": [{"date": "2026-01-02"}]}',
                json={"historical": [{"date": "2026-01-02"}]},
            ),
        ]
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret", retry_attempts=2), http_client=transport)

        result = client.fetch_historical_ohlcv_raw("AAPL", start_date="2026-01-01", end_date="2026-01-31")

        self.assertEqual(result, [{"date": "2026-01-02"}])
        self.assertEqual(transport.request.call_count, 2)
