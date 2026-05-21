import unittest

from app.vendors.fred.client import FredClientConfig, UnsupportedFredClient
from app.vendors.fred.endpoints import series_metadata_path, series_observations_path
from app.vendors.fred.mapper import fred_observation_to_normalized_macro, fred_series_metadata_to_dict


class FredVendorFoundationTests(unittest.TestCase):
    def test_endpoint_query_builders(self) -> None:
        self.assertEqual(series_observations_path("CPIAUCSL"), "/fred/series/observations?series_id=CPIAUCSL")
        self.assertEqual(series_metadata_path("CPIAUCSL"), "/fred/series?series_id=CPIAUCSL")

    def test_observation_mapping(self) -> None:
        record = fred_observation_to_normalized_macro({"series_id": "CPIAUCSL", "date": "2026-01-01", "value": "2.7"})
        self.assertEqual(record.symbol, "CPIAUCSL")
        self.assertEqual(record.value, 2.7)

    def test_series_metadata_shape(self) -> None:
        metadata = fred_series_metadata_to_dict({"series_id": "CPIAUCSL", "title": "CPI"})
        self.assertEqual(metadata["series_id"], "CPIAUCSL")
        self.assertEqual(metadata["title"], "CPI")

    def test_client_skeleton_does_not_perform_live_http_by_default(self) -> None:
        client = UnsupportedFredClient(FredClientConfig(api_key="test"))
        with self.assertRaises(NotImplementedError):
            client.fetch_series_observations("CPIAUCSL")
