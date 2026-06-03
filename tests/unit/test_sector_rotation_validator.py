import copy

from app.features.sector_rotation.sector_rotation_observation_builder import (
    SectorRotationBuildMetadata,
    SectorPriceSnapshot,
    build_sector_rotation_daily_summary_observation,
    build_sector_rotation_observation,
)
from app.features.sector_rotation.sector_leadership_engine import build_sector_leadership_snapshot
from app.features.sector_rotation.sector_rotation_summary_engine import build_sector_rotation_daily_summary
from app.features.sector_rotation.sector_rotation_validator import (
    validate_sector_rotation_daily_summaries,
    validate_sector_rotation_daily_summary,
    validate_sector_rotation_observation,
    validate_sector_rotation_observations,
)
from app.features.sector_rotation.sector_universe import get_spdr_sector_definitions


def _observation_row() -> dict[str, object]:
    definition = get_spdr_sector_definitions()[0]
    return build_sector_rotation_observation(
        definition,
        SectorPriceSnapshot(sector_symbol=definition.symbol, observation_date="2026-01-15", timestamp="2026-01-15T16:00:00Z", close=100.0),
        returns_by_window={"1d": {definition.symbol: 0.01}},
        relative_strength_by_window={"5d": {definition.symbol: 0.02}},
        leadership_snapshot=build_sector_leadership_snapshot({"5d": {definition.symbol: 0.02}, "20d": {definition.symbol: 0.01}, "60d": {definition.symbol: 0.005}}),
    )


def _summary_row() -> dict[str, object]:
    summary = build_sector_rotation_daily_summary(
        {"XLK": 0.3, "XLF": 0.2, "XLP": 0.1, "XLE": -0.1}
    )
    return build_sector_rotation_daily_summary_observation(
        {
            "observation_date": "2026-01-15",
            "timestamp": "2026-01-15T16:00:00Z",
            **summary,
        }
    )


def test_valid_sector_observation_passes() -> None:
    result = validate_sector_rotation_observation(_observation_row())
    assert result.is_valid is True
    assert result.errors == ()


def test_missing_required_field_fails() -> None:
    row = _observation_row()
    row.pop("source")
    result = validate_sector_rotation_observation(row)
    assert result.is_valid is False
    assert any(error.field == "source" for error in result.errors)


def test_spy_as_sector_symbol_fails() -> None:
    row = _observation_row()
    row["sector_symbol"] = "SPY"
    result = validate_sector_rotation_observation(row)
    assert result.is_valid is False


def test_unknown_sector_symbol_fails() -> None:
    row = _observation_row()
    row["sector_symbol"] = "XYZ"
    result = validate_sector_rotation_observation(row)
    assert result.is_valid is False


def test_invalid_close_fails() -> None:
    row = _observation_row()
    row["close"] = -1
    result = validate_sector_rotation_observation(row)
    assert result.is_valid is False


def test_invalid_rank_fails() -> None:
    row = _observation_row()
    row["rank_5d"] = 0
    result = validate_sector_rotation_observation(row)
    assert result.is_valid is False


def test_invalid_flag_fails() -> None:
    row = _observation_row()
    row["leadership_flag"] = "yes"
    result = validate_sector_rotation_observation(row)
    assert result.is_valid is False


def test_duplicate_sector_observation_key_fails() -> None:
    row = _observation_row()
    result = validate_sector_rotation_observations([row, copy.deepcopy(row)])
    assert result.is_valid is False
    assert any(error.code == "duplicate_row" for error in result.errors)


def test_valid_daily_summary_passes() -> None:
    result = validate_sector_rotation_daily_summary(_summary_row())
    assert result.is_valid is True


def test_invalid_descriptive_state_fails() -> None:
    row = _summary_row()
    row["descriptive_rotation_state"] = "BULLISH"
    result = validate_sector_rotation_daily_summary(row)
    assert result.is_valid is False


def test_invalid_top_bottom_sector_symbol_fails() -> None:
    row = _summary_row()
    row["top_sector_symbols"] = ["XLK", "XYZ"]
    result = validate_sector_rotation_daily_summary(row)
    assert result.is_valid is False


def test_duplicate_daily_summary_key_fails() -> None:
    row = _summary_row()
    result = validate_sector_rotation_daily_summaries([row, copy.deepcopy(row)])
    assert result.is_valid is False
    assert any(error.code == "duplicate_row" for error in result.errors)


def test_validator_does_not_mutate_input() -> None:
    row = _observation_row()
    snapshot = copy.deepcopy(row)
    validate_sector_rotation_observation(row)
    assert row == snapshot

