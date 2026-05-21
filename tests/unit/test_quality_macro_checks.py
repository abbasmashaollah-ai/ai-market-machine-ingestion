import unittest
from datetime import datetime

from app.models.normalized import NormalizedMacroObservation
from app.quality.macro_checks import validate_macro_observation


class MacroQualityTests(unittest.TestCase):
    def test_invalid_macro_observation(self) -> None:
        record = NormalizedMacroObservation(
            symbol=None,
            symbol_id=None,
            timestamp=datetime(2026, 1, 1, 14, 30),
            value=None,
        )

        results = validate_macro_observation(record)
        self.assertTrue(any(not result.passed for result in results))
