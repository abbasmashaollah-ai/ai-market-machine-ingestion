from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from app.vendors.common.http import UrlLibHttpClient
from app.vendors.fred.client import FredClientConfig, UnsupportedFredClient


DEFAULT_SERIES = ("GDP", "CPIAUCSL", "UNRATE")


@dataclass(frozen=True)
class ProbeSummary:
    series_id: str
    row_count: int
    first_date: str | None
    last_date: str | None


def build_default_window(days: int = 14) -> tuple[str, str]:
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date.isoformat(), end_date.isoformat()


def summarize_observations(series_id: str, observations: list[dict[str, object]]) -> ProbeSummary:
    dates = [str(row.get("date")) for row in observations if row.get("date")]
    return ProbeSummary(
        series_id=series_id,
        row_count=len(observations),
        first_date=dates[0] if dates else None,
        last_date=dates[-1] if dates else None,
    )


def run_probe(
    *,
    series_ids: tuple[str, ...] = DEFAULT_SERIES,
    observation_start: str | None = None,
    observation_end: str | None = None,
    client: UnsupportedFredClient | None = None,
) -> list[ProbeSummary]:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY is required")
    if client is None:
        client = UnsupportedFredClient(FredClientConfig(api_key=api_key), http_client=UrlLibHttpClient())
    if observation_start is None or observation_end is None:
        observation_start, observation_end = build_default_window()

    summaries: list[ProbeSummary] = []
    for series_id in series_ids:
        observations = client.fetch_series_observations_raw(
            series_id,
            observation_start=observation_start,
            observation_end=observation_end,
        )
        summaries.append(summarize_observations(series_id, observations))
    return summaries


def _write_output(path: str, summaries: list[ProbeSummary]) -> None:
    payload = [summary.__dict__ for summary in summaries]
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe FRED series connectivity.")
    parser.add_argument("--series", nargs="*", default=list(DEFAULT_SERIES))
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    observation_start, observation_end = build_default_window(args.days)
    summaries = run_probe(
        series_ids=tuple(args.series),
        observation_start=observation_start,
        observation_end=observation_end,
    )
    for summary in summaries:
        print(
            f"series_id={summary.series_id} row_count={summary.row_count} "
            f"first_date={summary.first_date} last_date={summary.last_date}"
        )
    if args.output:
        _write_output(args.output, summaries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
