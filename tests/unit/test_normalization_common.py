import unittest
from datetime import date, datetime, timezone

from app.normalization.common import safe_bool, safe_date, safe_datetime, safe_decimal, safe_number, safe_text


class NormalizationCommonTests(unittest.TestCase):
    def test_safe_text(self) -> None:
        self.assertEqual(safe_text("  abc "), "abc")
        self.assertIsNone(safe_text("   "))

    def test_safe_bool(self) -> None:
        self.assertTrue(safe_bool("yes"))
        self.assertFalse(safe_bool("no"))
        self.assertTrue(safe_bool(1))
        self.assertFalse(safe_bool(0))

    def test_safe_decimal_and_number(self) -> None:
        self.assertEqual(str(safe_decimal("12.5")), "12.5")
        self.assertEqual(safe_number("12.5"), 12.5)

    def test_safe_date(self) -> None:
        self.assertEqual(safe_date("2026-01-02"), date(2026, 1, 2))

    def test_safe_datetime_normalizes_timezone(self) -> None:
        dt = safe_datetime("2026-01-02T10:00:00-08:00")
        self.assertEqual(dt.tzinfo, timezone.utc)
        self.assertEqual(dt.hour, 18)
