import copy

from app.features.sector_rotation.sector_rotation_observation_builder import (
    build_sector_rotation_daily_summary_observation,
    build_sector_rotation_observation,
)
from app.features.sector_rotation.sector_rotation_summary_engine import build_sector_rotation_daily_summary
from app.features.sector_rotation.sector_rotation_validator import validate_sector_rotation_observation
from app.features.sector_rotation.sector_rotation_writer import SectorRotationMockWriter, write_sector_rotation_payloads
from app.features.sector_rotation.sector_universe import get_spdr_sector_definitions
from app.features.sector_rotation.sector_leadership_engine import build_sector_leadership_snapshot


def _observation_row() -> dict[str, object]:
    definition = get_spdr_sector_definitions()[0]
    return build_sector_rotation_observation(
        definition,
        {"sector_symbol": definition.symbol, "observation_date": "2026-01-15", "timestamp": "2026-01-15T16:00:00Z", "close": 100.0},
        returns_by_window={"1d": {definition.symbol: 0.01}},
        relative_strength_by_window={"5d": {definition.symbol: 0.02}},
        leadership_snapshot=build_sector_leadership_snapshot({"5d": {definition.symbol: 0.02}, "20d": {definition.symbol: 0.01}, "60d": {definition.symbol: 0.005}}),
    )


def _summary_row() -> dict[str, object]:
    summary = build_sector_rotation_daily_summary({"XLK": 0.3, "XLF": 0.2, "XLP": 0.1, "XLE": -0.1})
    return build_sector_rotation_daily_summary_observation(
        {
            "observation_date": "2026-01-15",
            "timestamp": "2026-01-15T16:00:00Z",
            **summary,
        }
    )


def test_valid_rows_are_accepted_by_mock_writer() -> None:
    writer = SectorRotationMockWriter()
    result = writer.write(observation_rows=[_observation_row()], summary_rows=[_summary_row()])

    assert result.accepted_observation_count == 1
    assert result.accepted_summary_count == 1
    assert result.rejected_observation_count == 0
    assert result.rejected_summary_count == 0
    assert writer.observation_rows and writer.summary_rows
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True


def test_invalid_observation_row_is_rejected() -> None:
    row = _observation_row()
    row["close"] = -1
    writer = SectorRotationMockWriter()
    result = writer.write(observation_rows=[row], summary_rows=[_summary_row()])

    assert result.accepted_observation_count == 0
    assert result.rejected_observation_count == 1
    assert any(error.field == "close" for error in result.errors)
    assert writer.observation_rows == []


def test_invalid_summary_row_is_rejected() -> None:
    row = _summary_row()
    row["descriptive_rotation_state"] = "BULLISH"
    writer = SectorRotationMockWriter()
    result = writer.write(observation_rows=[_observation_row()], summary_rows=[row])

    assert result.accepted_summary_count == 0
    assert result.rejected_summary_count == 1
    assert any(error.field == "descriptive_rotation_state" for error in result.errors)
    assert writer.summary_rows == []


def test_input_rows_are_not_mutated() -> None:
    observation_row = _observation_row()
    summary_row = _summary_row()
    observation_snapshot = copy.deepcopy(observation_row)
    summary_snapshot = copy.deepcopy(summary_row)
    writer = SectorRotationMockWriter()
    writer.write(observation_rows=[observation_row], summary_rows=[summary_row])
    assert observation_row == observation_snapshot
    assert summary_row == summary_snapshot


def test_no_db_dependency_by_construction() -> None:
    writer = SectorRotationMockWriter()
    result = write_sector_rotation_payloads([_observation_row()], [_summary_row()], writer=writer)
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True

