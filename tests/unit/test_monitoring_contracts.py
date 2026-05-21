import unittest

from app.monitoring.alerts import (
    AlertSeverity,
    AlertEvent,
    db_write_failure,
    daily_ingestion_failure,
    excessive_quality_failures,
    stuck_checkpoint,
    vendor_outage,
)
from app.monitoring.logging_context import build_logging_context
from app.monitoring.metrics import build_metric_event, MetricEvent


class MonitoringContractTests(unittest.TestCase):
    def test_metric_event_shape(self) -> None:
        event = build_metric_event("rows_fetched", 10, "count", run_id="run-1", vendor="polygon")
        self.assertIsInstance(event, MetricEvent)
        self.assertEqual(event.name, "rows_fetched")
        self.assertEqual(event.value, 10)
        self.assertEqual(event.vendor, "polygon")

    def test_alert_event_shape(self) -> None:
        event = AlertEvent(alert_type="vendor_outage", severity=AlertSeverity.HIGH, message="vendor outage")
        self.assertEqual(event.alert_type, "vendor_outage")
        self.assertEqual(event.severity, AlertSeverity.HIGH)

    def test_alert_helpers(self) -> None:
        self.assertEqual(daily_ingestion_failure().alert_type, "daily_ingestion_failure")
        self.assertEqual(stuck_checkpoint().alert_type, "stuck_checkpoint")
        self.assertEqual(vendor_outage().alert_type, "vendor_outage")
        self.assertEqual(db_write_failure().severity, AlertSeverity.CRITICAL)
        self.assertEqual(excessive_quality_failures().alert_type, "excessive_quality_failures")

    def test_logging_context_shape(self) -> None:
        context = build_logging_context(
            run_id="run-1",
            vendor="polygon",
            dataset="ohlcv",
            symbol="AAPL",
            timeframe="1d",
            job_id="job-1",
            status="running",
        )
        self.assertEqual(context["run_id"], "run-1")
        self.assertEqual(context["job_id"], "job-1")
