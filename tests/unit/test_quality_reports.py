import unittest

from app.quality.reports import validation_results_to_report
from app.quality.validators import pass_result, summarize_results


class QualityReportTests(unittest.TestCase):
    def test_report_dict_conversion(self) -> None:
        results = [pass_result("a"), pass_result("b")]
        summary = summarize_results(results)
        report = validation_results_to_report(results, summary)

        self.assertEqual(report["total_checks"], 2)
        self.assertEqual(report["overall_status"], "pass")
