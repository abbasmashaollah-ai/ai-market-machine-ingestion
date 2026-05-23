from __future__ import annotations

import argparse


def _request_budget_status(*, estimated_requests: int, max_requests: int) -> str:
    return "within_budget" if estimated_requests <= max_requests else "exceeds_budget"


def _recommended_source_path(source_mode: str) -> str:
    if source_mode == "api":
        return "recent/daily/gap data and small controlled backfills"
    if source_mode == "flatfiles":
        return "large historical downloads/backfills"
    return "future live streaming data"


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon quota readiness safely.")
    parser.add_argument("--estimated-requests", type=int, required=True, help="Estimated vendor request count.")
    parser.add_argument("--max-requests", type=int, required=True, help="Maximum allowed request count.")
    parser.add_argument("--sleep-seconds-between-requests", type=float, required=True, help="Sleep seconds between requests.")
    parser.add_argument("--source-mode", choices=("api", "flatfiles", "websocket"), default="api", help="Polygon source mode.")
    args = parser.parse_args()

    request_budget_status = _request_budget_status(
        estimated_requests=args.estimated_requests,
        max_requests=args.max_requests,
    )
    quota_readiness_status = "ready" if request_budget_status == "within_budget" else "manual_review_needed"
    print(f"source_mode={args.source_mode}")
    print(f"estimated_requests={args.estimated_requests}")
    print(f"max_requests={args.max_requests}")
    print(f"request_budget_status={request_budget_status}")
    print(f"sleep_seconds_between_requests={args.sleep_seconds_between_requests}")
    print(f"quota_readiness_status={quota_readiness_status}")
    print(f"recommended_source_path={_recommended_source_path(args.source_mode)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
