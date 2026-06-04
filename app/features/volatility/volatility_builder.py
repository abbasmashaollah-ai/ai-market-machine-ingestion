"""Build JSON-friendly volatility observations from fixture histories."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.volatility.volatility_engine import (
    calculate_composite_volatility_stress_score,
    calculate_equity_volatility_pressure_score,
    calculate_latest_level,
    calculate_nasdaq_volatility_pressure_score,
    calculate_series_change,
    calculate_small_cap_volatility_pressure_score,
    calculate_volatility_of_volatility_score,
    determine_volatility_regime_label,
)
from app.features.volatility.volatility_universe import get_required_volatility_series


def _normalize_date(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _metadata_dict(metadata: Mapping[str, object] | None) -> dict[str, object]:
    result = dict(metadata or {})
    result.setdefault("quality_status", "PENDING")
    result.setdefault("certification_status", "PENDING")
    result.setdefault("freshness_status", "PENDING")
    result.setdefault("source_attribution", "fixture_volatility")
    result.setdefault("dataset_version", "volatility_dry_run_v1")
    result.setdefault("lineage", {})
    result.setdefault("evidence", {})
    return result


def _stable_metadata_timestamp(value: str | None, observation_date: str | None, fallback_suffix: str) -> str | None:
    if value is not None:
        return value
    if observation_date is None:
        return None
    return f"{observation_date}T00:00:00Z[{fallback_suffix}]"


def _series_values(history) -> list[float]:
    values = [row["close"] if isinstance(row, Mapping) else row for row in history]
    return [float(value) for value in values if isinstance(value, (int, float))]


def build_volatility_observation(
    series_history_by_name,
    observation_date,
    timestamp=None,
    source="fixture_volatility",
    metadata: Mapping[str, object] | None = None,
):
    required_series = get_required_volatility_series()
    series_keys = {str(name).upper() for name in series_history_by_name}

    series_map: dict[str, list[object]] = {}
    latest_levels: dict[str, float | None] = {}
    for series in required_series:
        history = list(series_history_by_name.get(series, []))
        series_map[series] = history
        latest_levels[series] = calculate_latest_level(_series_values(history))

    vix_values = _series_values(series_map["VIX"])
    vvix_values = _series_values(series_map["VVIX"])
    vxn_values = _series_values(series_map["VXN"])
    rvx_values = _series_values(series_map["RVX"])

    vix_change_1d = calculate_series_change(vix_values, 1)
    vix_change_5d = calculate_series_change(vix_values, 5)
    vix_change_20d = calculate_series_change(vix_values, 20)
    vvix_change_5d = calculate_series_change(vvix_values, 5)
    vxn_change_5d = calculate_series_change(vxn_values, 5)
    rvx_change_5d = calculate_series_change(rvx_values, 5)

    component_scores = {
        "volatility_of_volatility_score": calculate_volatility_of_volatility_score(vvix_level=latest_levels["VVIX"], vvix_change_5d=vvix_change_5d),
        "equity_volatility_pressure_score": calculate_equity_volatility_pressure_score(vix_level=latest_levels["VIX"], vix_change_5d=vix_change_5d),
        "nasdaq_volatility_pressure_score": calculate_nasdaq_volatility_pressure_score(vxn_level=latest_levels["VXN"], vxn_change_5d=vxn_change_5d),
        "small_cap_volatility_pressure_score": calculate_small_cap_volatility_pressure_score(rvx_level=latest_levels["RVX"], rvx_change_5d=rvx_change_5d),
    }
    composite_score = calculate_composite_volatility_stress_score(component_scores)
    volatility_regime_label = determine_volatility_regime_label(vix_level=latest_levels["VIX"], composite_score=composite_score)

    payload = {
        "observation_date": _normalize_date(observation_date),
        "timestamp": _normalize_date(timestamp),
        "series": sorted(series_keys),
        "vix_level": latest_levels["VIX"],
        "vvix_level": latest_levels["VVIX"],
        "vxn_level": latest_levels["VXN"],
        "rvx_level": latest_levels["RVX"],
        "vix_change_1d": vix_change_1d,
        "vix_change_5d": vix_change_5d,
        "vix_change_20d": vix_change_20d,
        "vvix_change_5d": vvix_change_5d,
        "volatility_of_volatility_score": component_scores["volatility_of_volatility_score"],
        "equity_volatility_pressure_score": component_scores["equity_volatility_pressure_score"],
        "nasdaq_volatility_pressure_score": component_scores["nasdaq_volatility_pressure_score"],
        "small_cap_volatility_pressure_score": component_scores["small_cap_volatility_pressure_score"],
        "composite_volatility_stress_score": composite_score,
        "volatility_regime_label": volatility_regime_label,
        "source": source,
    }
    payload["vix_close"] = payload["vix_level"]
    payload["vvix_close"] = payload["vvix_level"]
    payload["vxn_close"] = payload["vxn_level"]
    payload["rvx_close"] = payload["rvx_level"]
    payload["volatility_stress_score"] = payload["composite_volatility_stress_score"]
    payload["descriptive_volatility_state"] = payload["volatility_regime_label"]
    metadata_dict = _metadata_dict(metadata if isinstance(metadata, Mapping) else None)
    payload.update(
        {
            "quality_status": metadata_dict["quality_status"],
            "certification_status": metadata_dict["certification_status"],
            "freshness_status": metadata_dict["freshness_status"],
            "source_attribution": metadata_dict.get("source_attribution"),
            "dataset_version": metadata_dict.get("dataset_version"),
            "created_at": _stable_metadata_timestamp(
                metadata_dict.get("created_at"),
                payload.get("observation_date"),
                "created_at",
            ),
            "updated_at": _stable_metadata_timestamp(
                metadata_dict.get("updated_at"),
                payload.get("observation_date"),
                "updated_at",
            ),
            "lineage": metadata_dict["lineage"],
            "evidence": metadata_dict["evidence"],
        }
    )
    return payload
