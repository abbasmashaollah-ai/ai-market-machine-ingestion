from copy import deepcopy

from app.features.cross_asset.cross_asset_builder import build_cross_asset_observation
from app.features.cross_asset.cross_asset_writer import CrossAssetMockWriter, write_cross_asset_payloads
from tests.fixtures.cross_asset_ohlcv import build_cross_asset_ohlcv_fixtures


def test_writer_accepts_valid_rows() -> None:
    observation = build_cross_asset_observation(build_cross_asset_ohlcv_fixtures(), "2026-01-15")
    writer = CrossAssetMockWriter()
    result = write_cross_asset_payloads([observation], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert len(writer.accepted_rows) == 1


def test_writer_does_not_mutate_inputs() -> None:
    observation = build_cross_asset_observation(build_cross_asset_ohlcv_fixtures(), "2026-01-15")
    snapshot = deepcopy(observation)
    write_cross_asset_payloads([observation], writer=CrossAssetMockWriter())
    assert observation == snapshot