import unittest

from app.vendors.fred.series_catalog import (
    SERIES_CATALOG,
    FREDSeriesDefinition,
    SeriesCategory,
    get_active_series,
    get_series_by_category,
    get_series_definition,
)


class FredSeriesCatalogTests(unittest.TestCase):
    def test_catalog_is_non_empty(self) -> None:
        self.assertGreater(len(SERIES_CATALOG), 0)

    def test_all_series_ids_are_unique(self) -> None:
        series_ids = [series.series_id for series in SERIES_CATALOG]
        self.assertEqual(len(series_ids), len(set(series_ids)))

    def test_active_series_helper(self) -> None:
        active_series = get_active_series()
        self.assertTrue(all(series.active for series in active_series))
        self.assertGreater(len(active_series), 0)

    def test_category_filtering(self) -> None:
        inflation_series = get_series_by_category(SeriesCategory.INFLATION)
        self.assertTrue(all(series.category == SeriesCategory.INFLATION for series in inflation_series))
        self.assertGreater(len(inflation_series), 0)

    def test_lookup_by_series_id(self) -> None:
        series = get_series_definition("gdp")
        self.assertIsNotNone(series)
        self.assertEqual(series.series_id, "GDP")

    def test_priority_values_are_valid(self) -> None:
        self.assertTrue(all(isinstance(series.priority, int) and series.priority > 0 for series in SERIES_CATALOG))
        self.assertTrue(all(isinstance(series, FREDSeriesDefinition) for series in SERIES_CATALOG))
