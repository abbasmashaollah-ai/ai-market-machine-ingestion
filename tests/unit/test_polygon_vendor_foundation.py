import unittest

from app.vendors.polygon.client import PolygonClientConfig, UnsupportedPolygonClient
from app.vendors.polygon.endpoints import daily_aggregates_path, reference_tickers_path, ticker_details_path
from app.vendors.polygon.mapper import polygon_aggregate_to_normalized_ohlcv, polygon_ticker_to_normalized_symbol
from app.vendors.polygon.rate_limiter import PolygonRateLimiter
from app.vendors.polygon.retry import build_retry_policy


class PolygonVendorFoundationTests(unittest.TestCase):
    def test_endpoint_path_builders(self) -> None:
        self.assertEqual(daily_aggregates_path("AAPL", "2026-01-01", "2026-01-31"), "/v2/aggs/ticker/AAPL/range/1/day/2026-01-01/2026-01-31")
        self.assertEqual(ticker_details_path("AAPL"), "/v3/reference/tickers/AAPL")
        self.assertEqual(reference_tickers_path(), "/v3/reference/tickers")

    def test_polygon_aggregate_mapping(self) -> None:
        record = polygon_aggregate_to_normalized_ohlcv(
            {"ticker": "AAPL", "t": 1767264000000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True}
        )
        self.assertEqual(record.symbol, "AAPL")
        self.assertTrue(record.adjusted)

    def test_polygon_ticker_mapping(self) -> None:
        record = polygon_ticker_to_normalized_symbol({"ticker": "AAPL", "type": "CS", "primary_exchange": "XNAS", "active": True})
        self.assertEqual(record.symbol, "AAPL")
        self.assertEqual(record.exchange, "XNAS")

    def test_retry_policy_shape(self) -> None:
        policy = build_retry_policy(max_attempts=5, backoff_seconds=2.0, jitter=True)
        self.assertEqual(policy.max_attempts, 5)
        self.assertTrue(policy.jitter)

    def test_rate_limiter_construction(self) -> None:
        limiter = PolygonRateLimiter(60)
        self.assertTrue(limiter.allow(now=0))

    def test_client_skeleton_does_not_perform_live_http_by_default(self) -> None:
        client = UnsupportedPolygonClient(PolygonClientConfig(api_key="test"))
        with self.assertRaises(NotImplementedError):
            client.fetch_aggregates("AAPL", "2026-01-01", "2026-01-31")
