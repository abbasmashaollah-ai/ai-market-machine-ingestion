from __future__ import annotations

from urllib.parse import urlencode


def series_observations_path(series_id: str) -> str:
    return f"/fred/series/observations?{urlencode({'series_id': series_id})}"


def series_metadata_path(series_id: str) -> str:
    return f"/fred/series?{urlencode({'series_id': series_id})}"


def series_observations_params(api_key: str | None = None, *, observation_start: str | None = None, observation_end: str | None = None) -> dict[str, str]:
    params: dict[str, str] = {}
    if api_key is not None:
        params["api_key"] = api_key
    if observation_start is not None:
        params["observation_start"] = observation_start
    if observation_end is not None:
        params["observation_end"] = observation_end
    return params


def series_metadata_params(api_key: str | None = None) -> dict[str, str]:
    params: dict[str, str] = {}
    if api_key is not None:
        params["api_key"] = api_key
    return params


def series_observations_query(
    api_key: str | None = None,
    *,
    observation_start: str | None = None,
    observation_end: str | None = None,
) -> dict[str, str]:
    params: dict[str, str] = {}
    if api_key is not None:
        params["api_key"] = api_key
    if observation_start is not None:
        params["observation_start"] = observation_start
    if observation_end is not None:
        params["observation_end"] = observation_end
    return params
