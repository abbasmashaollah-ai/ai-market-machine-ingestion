import json

from app.features.cross_asset.cross_asset_builder import build_cross_asset_observation
from app.features.cross_asset.cross_asset_report import build_cross_asset_report
from app.features.cross_asset.cross_asset_writer import CrossAssetMockWriter, write_cross_asset_payloads
from tests.fixtures.cross_asset_ohlcv import build_cross_asset_ohlcv_fixtures


def test_report_contains_expected_fields() -> None:
    observation = build_cross_asset_observation(build_cross_asset_ohlcv_fixtures(), "2026-01-15")
    writer_result = write_cross_asset_payloads([observation], writer=CrossAssetMockWriter())
    report = build_cross_asset_report(observation, writer_result=writer_result)
    assert report["descriptive_intermarket_state"]
    assert report["accepted_count"] == 1
    assert report["no_db_writes"] is True
    json.dumps(report)