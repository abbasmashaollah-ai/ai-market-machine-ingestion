import unittest
from datetime import date

from app.state.checkpoints import CheckpointStatus, IngestionCheckpoint
from app.state.errors import IngestionErrorRecord
from app.state.jobs import IngestionJob, JobStatus, transition_job_status
from app.state.runs import IngestionRun, RunStatus


class StateContractTests(unittest.TestCase):
    def test_job_status_values(self) -> None:
        self.assertEqual(JobStatus.PENDING.value, "pending")
        self.assertEqual(JobStatus.RUNNING.value, "running")
        self.assertEqual(JobStatus.SUCCESS.value, "success")
        self.assertEqual(JobStatus.FAILED.value, "failed")

    def test_checkpoint_construction(self) -> None:
        checkpoint = IngestionCheckpoint(checkpoint_id="cp-1", job_id="job-1", last_successful_date=date(2026, 1, 1))
        self.assertEqual(checkpoint.status, CheckpointStatus.PENDING)
        self.assertEqual(checkpoint.last_successful_date, date(2026, 1, 1))

    def test_run_counters_and_summary(self) -> None:
        run = IngestionRun(run_id="run-1", job_id="job-1", rows_fetched=10, rows_written=7, rows_rejected=3, error_count=1)
        self.assertEqual(run.rows_total, 10)
        self.assertEqual(run.rows_processed, 10)
        self.assertTrue(run.has_errors)

    def test_error_record_shape(self) -> None:
        record = IngestionErrorRecord(
            error_id="err-1",
            run_id="run-1",
            error_type="vendor_timeout",
            message="timeout",
            retryable=True,
        )
        self.assertTrue(record.retryable)
        self.assertEqual(record.error_type, "vendor_timeout")

    def test_safe_job_transition(self) -> None:
        self.assertEqual(transition_job_status(JobStatus.PENDING, JobStatus.RUNNING), JobStatus.RUNNING)
        with self.assertRaises(ValueError):
            transition_job_status(JobStatus.SUCCESS, JobStatus.RUNNING)
