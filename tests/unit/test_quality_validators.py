import unittest

from app.quality.validators import ValidationStatus, pass_result, summarize_results, warn_result


class QualityValidatorTests(unittest.TestCase):
    def test_batch_summary(self) -> None:
        results = [
            pass_result("a"),
            warn_result("b", "warn"),
            pass_result("c"),
        ]
        summary = summarize_results(results)

        self.assertEqual(summary.total_checks, 3)
        self.assertEqual(summary.passed_checks, 2)
        self.assertEqual(summary.warning_checks, 1)
        self.assertFalse(summary.failed)
