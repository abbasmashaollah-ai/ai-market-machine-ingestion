import unittest

from app.normalization.macro import normalize_macro_observation


class MacroNormalizationTests(unittest.TestCase):
    def test_normalize_macro_dict(self) -> None:
        record = normalize_macro_observation(
            {
                "symbol": "CPI",
                "timestamp": "2026-01-02T08:30:00Z",
                "value": "2.7",
                "vendor": "fred",
                "source": "macro",
                "quality_status": "pending",
            }
        )

        self.assertEqual(record.symbol, "CPI")
        self.assertEqual(record.timeframe, "1d")
        self.assertEqual(record.value, 2.7)

    def test_missing_timestamp_raises(self) -> None:
        with self.assertRaises(ValueError):
            normalize_macro_observation({})
