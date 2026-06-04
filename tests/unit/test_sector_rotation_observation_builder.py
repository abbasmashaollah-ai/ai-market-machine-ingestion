import pytest

from app.features.sector_rotation.sector_leadership_engine import build_sector_leadership_snapshot
from app.features.sector_rotation.sector_rotation_observation_builder import (
    SectorRotationBuildMetadata,
    SectorPriceSnapshot,
    build_sector_rotation_daily_summary_observation,
    build_sector_rotation_observation,
    build_sector_rotation_observations,
)
from app.features.sector_rotation.sector_universe import get_spdr_sector_definitions


def _leadership_snapshot() -> dict[str, dict[str, object]]:
    return build_sector_leadership_snapshot(
        {
            "5d": {"XLK": 0.3, "XLF": 0.2, "XLP": 0.1},
            "20d": {"XLK": 0.2, "XLF": 0.1, "XLP": 0.05},
            "60d": {"XLK": 0.1, "XLF": 0.05, "XLP": 0.02},
        }
    )


def test_single_sector_row_includes_all_required_fields() -> None:
    definition = get_spdr_sector_definitions()[0]
    row = build_sector_rotation_observation(
        definition,
        SectorPriceSnapshot(sector_symbol="xlc", observation_date="2026-01-15", timestamp="2026-01-15T16:00:00Z", close=100.0),
        returns_by_window={"1d": {"XLC": 0.01}},
        relative_strength_by_window={"5d": {"XLC": 0.02}},
        leadership_snapshot=_leadership_snapshot(),
    )

    required_fields = {
        "universe",
        "sector",
        "sector_symbol",
        "observation_date",
        "timestamp",
        "close",
        "return_1d",
        "return_5d",
        "return_20d",
        "return_60d",
        "relative_strength_5d_vs_spy",
        "relative_strength_20d_vs_spy",
        "relative_strength_60d_vs_spy",
        "rank_5d",
        "rank_20d",
        "rank_60d",
        "rank_change_5d",
        "rank_change_20d",
        "momentum_score",
        "leadership_flag",
        "deterioration_flag",
        "is_defensive_sector",
        "is_cyclical_sector",
        "is_growth_sector",
        "is_rate_sensitive_sector",
        "source",
        "source_attribution",
        "lineage",
        "quality_status",
        "certification_status",
        "freshness_status",
        "evidence",
    }
    assert set(row) == required_fields
    assert row["sector_symbol"] == "XLC"
    assert row["sector"] == "Communication Services"
    assert row["is_growth_sector"] is True


def test_all_sector_builder_excludes_spy_and_preserves_order() -> None:
    metadata = SectorRotationBuildMetadata()
    metadata = SectorRotationBuildMetadata(
        universe=metadata.universe,
        source=metadata.source,
        source_attribution=metadata.source_attribution,
        quality_status=metadata.quality_status,
        certification_status=metadata.certification_status,
        freshness_status=metadata.freshness_status,
        lineage=metadata.lineage,
        evidence=metadata.evidence,
    )
    metadata_dict = {
        "observation_date": "2026-01-15",
        "timestamp": "2026-01-15T16:00:00Z",
        "universe": metadata.universe,
        "source": metadata.source,
        "source_attribution": metadata.source_attribution,
        "quality_status": metadata.quality_status,
        "certification_status": metadata.certification_status,
        "freshness_status": metadata.freshness_status,
        "lineage": {},
        "evidence": {},
    }
    rows = build_sector_rotation_observations(
        {"SPY": 500.0, "XLC": 100.0, "XLY": 101.0, "XLP": 99.0},
        returns_by_symbol_by_window={"5d": {"XLC": 0.01, "XLY": 0.02, "XLP": 0.03}},
        relative_strength_by_window={"5d": {"XLC": 0.01, "XLY": 0.02, "XLP": 0.03}},
        leadership_snapshot=_leadership_snapshot(),
        metadata=metadata_dict,
    )

    assert [row["sector_symbol"] for row in rows] == [definition.symbol for definition in get_spdr_sector_definitions()]
    assert all(row["sector_symbol"] != "SPY" for row in rows)


def test_missing_optional_metric_values_become_none() -> None:
    row = build_sector_rotation_observation(
        get_spdr_sector_definitions()[0],
        {"sector_symbol": "XLC", "observation_date": "2026-01-15", "timestamp": "2026-01-15T16:00:00Z", "close": 100.0},
    )
    assert row["return_1d"] is None
    assert row["relative_strength_5d_vs_spy"] is None


def test_missing_required_observation_date_raises() -> None:
    with pytest.raises(ValueError):
        build_sector_rotation_observation(
            get_spdr_sector_definitions()[0],
            {"sector_symbol": "XLC", "timestamp": "2026-01-15T16:00:00Z", "close": 100.0},
        )


def test_summary_row_includes_expected_fields_and_defaults() -> None:
    summary = build_sector_rotation_daily_summary_observation(
        {
            "observation_date": "2026-01-15",
            "timestamp": "2026-01-15T16:00:00Z",
            "descriptive_rotation_state": "BROAD_IMPROVEMENT",
            "risk_on_leadership_score": 0.7,
            "cyclical_leadership_score": 0.65,
            "defensive_leadership_score": 0.3,
            "leadership_concentration_score": 0.6,
            "sector_dispersion_score": 0.2,
            "broad_rotation_flag": True,
            "narrow_rotation_flag": False,
            "improving_rotation_flag": True,
            "deteriorating_rotation_flag": False,
            "top_sector_symbols": ["XLK", "XLY"],
            "bottom_sector_symbols": ["XLE", "XLP"],
        }
    )

    assert summary["universe"] == "SPDR_SECTORS"
    assert summary["source"] == "canonical_ohlcv"
    assert summary["quality_status"] == "PENDING"
    assert summary["certification_status"] == "PENDING"
    assert summary["freshness_status"] == "PENDING"
    assert summary["cyclical_leadership_score"] == 0.65
    assert summary["top_sector_symbols"] == ["XLK", "XLY"]
    assert summary["bottom_sector_symbols"] == ["XLE", "XLP"]


def test_metadata_override_works_and_output_is_dict_json_friendly() -> None:
    summary = build_sector_rotation_daily_summary_observation(
        {
            "observation_date": "2026-01-15",
            "timestamp": "2026-01-15T16:00:00Z",
            "descriptive_rotation_state": "NO_CLEAR_ROTATION",
        },
        metadata={
            "universe": "SPDR_SECTORS",
            "source": "canonical_ohlcv",
            "source_attribution": "unit-test",
            "quality_status": "VALID",
            "certification_status": "UNCERTIFIED",
            "freshness_status": "UNKNOWN",
            "lineage": {"source": "test"},
            "evidence": {"note": "override"},
        },
    )

    assert summary["source_attribution"] == "unit-test"
    assert summary["quality_status"] == "VALID"
    assert isinstance(summary, dict)
