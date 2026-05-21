from __future__ import annotations

from urllib.parse import urlencode


def series_observations_path(series_id: str) -> str:
    return f"/fred/series/observations?{urlencode({'series_id': series_id})}"


def series_metadata_path(series_id: str) -> str:
    return f"/fred/series?{urlencode({'series_id': series_id})}"
