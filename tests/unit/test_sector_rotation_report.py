from datetime import datetime, timezone

from app.features.sector_rotation.sector_rotation_reader import run_sector_rotation_certified_ohlcv_dry_run
from app.features.sector_rotation.sector_rotation_report import build_sector_rotation_dry_run_report, summarize_sector_observations
from tests.fixtures.sector_rotation_ohlcv import build_fake_data_read_client_for_sector_rotation


def test_sector_rotation_dry_run_report_is_json_friendly_and_complete() -> None:
    client = build_fake_data_read_client_for_sector_rotation()
    dry_run_result = run_sector_rotation_certified_ohlcv_dry_run(
        client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )

    report = build_sector_rotation_dry_run_report(dry_run_result)

    assert isinstance(report, dict)
    assert report["top_sector_symbols"]
    assert report["bottom_sector_symbols"]
    assert report["accepted_observation_count"] == 11
    assert report["accepted_summary_count"] == 1
    assert report["no_db_writes"] is True
    assert report["no_vendor_calls"] is True
    assert report["no_scheduler_activation"] is True
    assert report["descriptive_rotation_state"]
    assert report["observation_summary"]["leadership_sectors"]
    assert report["observation_summary"]["deteriorating_sectors"] is not None


def test_sector_observation_summary_includes_role_lists() -> None:
    client = build_fake_data_read_client_for_sector_rotation()
    dry_run_result = run_sector_rotation_certified_ohlcv_dry_run(
        client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )

    summary = summarize_sector_observations(dry_run_result.dry_run_result.observation_rows)

    assert summary["strongest_sectors"]
    assert summary["weakest_sectors"]
    assert summary["leadership_sectors"]
    assert summary["deteriorating_sectors"]
    assert summary["defensive_represented"] is not None
    assert summary["cyclical_represented"] is not None
    assert summary["growth_represented"] is not None
    assert summary["rate_sensitive_represented"] is not None
