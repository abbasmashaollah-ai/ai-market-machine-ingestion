from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from app.vendors.common.http import UrlLibHttpClient
from app.vendors.fred.client import FredClientConfig, UnsupportedFredClient


DEFAULT_SERIES = ("GDP", "CPIAUCSL", "UNRATE")


@dataclass(frozen=True)
class ProbeSummary:
    series_id: str
    row_count: int
    first_date: str | None
    last_date: str | None


@dataclass(frozen=True)
class ProbeResult:
    summary: ProbeSummary
    payload: object


def load_local_env_if_available() -> bool:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    return bool(load_dotenv())


def build_default_window(days: int = 14) -> tuple[str, str]:
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date.isoformat(), end_date.isoformat()


def build_default_five_year_window() -> tuple[str, str]:
    end_date = date.today()
    start_date = end_date - timedelta(days=5 * 365)
    return start_date.isoformat(), end_date.isoformat()


def extract_observation_rows(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, dict) and isinstance(payload.get("observations"), list):
        return [row for row in payload["observations"] if isinstance(row, dict)]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    return []


def extract_safe_debug_details(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return {"response_keys": [], "fred_error": None}
    keys = sorted(str(key) for key in payload.keys())
    error_message = None
    for candidate_key in ("error_message", "message", "error"):
        value = payload.get(candidate_key)
        if isinstance(value, str) and value.strip():
            error_message = value.strip()
            break
    return {"response_keys": keys, "fred_error": error_message}


def summarize_observations(series_id: str, observations: list[dict[str, object]]) -> ProbeSummary:
    dates = [str(row.get("date")) for row in observations if row.get("date")]
    return ProbeSummary(
        series_id=series_id,
        row_count=len(observations),
        first_date=dates[0] if dates else None,
        last_date=dates[-1] if dates else None,
    )


def run_probe_details(
    *,
    series_ids: tuple[str, ...] = DEFAULT_SERIES,
    observation_start: str | None = None,
    observation_end: str | None = None,
    client: UnsupportedFredClient | None = None,
) -> list[ProbeResult]:
    load_local_env_if_available()
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY is required")
    if client is None:
        client = UnsupportedFredClient(FredClientConfig(api_key=api_key), http_client=UrlLibHttpClient())
    if observation_start is None or observation_end is None:
        observation_start, observation_end = build_default_five_year_window()

    results: list[ProbeResult] = []
    for series_id in series_ids:
        payload = client.fetch_series_observations_raw(
            series_id,
            observation_start=observation_start,
            observation_end=observation_end,
        )
        observations = extract_observation_rows(payload)
        summary = summarize_observations(series_id, observations)
        results.append(ProbeResult(summary=summary, payload=payload))
    return results


def run_probe(
    *,
    series_ids: tuple[str, ...] = DEFAULT_SERIES,
    observation_start: str | None = None,
    observation_end: str | None = None,
    client: UnsupportedFredClient | None = None,
) -> list[ProbeSummary]:
    return [result.summary for result in run_probe_details(
        series_ids=series_ids,
        observation_start=observation_start,
        observation_end=observation_end,
        client=client,
    )]


def _write_output(path: str, summaries: list[ProbeSummary]) -> None:
    payload = [summary.__dict__ for summary in summaries]
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe FRED series connectivity.")
    parser.add_argument("--series", nargs="*", default=list(DEFAULT_SERIES))
    parser.add_argument("--days", type=int, default=5 * 365)
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--debug-safe", action="store_true", help="Print safe debug details when a series has no rows.")
    args = parser.parse_args()

    observation_start, observation_end = build_default_window(args.days)
    results = run_probe_details(
        series_ids=tuple(args.series),
        observation_start=observation_start,
        observation_end=observation_end,
    )
    for result in results:
        summary = result.summary
        print(
            f"series_id={summary.series_id} row_count={summary.row_count} "
            f"first_date={summary.first_date} last_date={summary.last_date}"
        )
        if args.debug_safe and summary.row_count == 0:
            debug_details = extract_safe_debug_details(result.payload)
            print(
                f"response_keys={debug_details['response_keys']} "
                f"fred_error={debug_details['fred_error']}"
            )
    if args.output:
        _write_output(args.output, summaries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
