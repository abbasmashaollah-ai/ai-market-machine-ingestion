from __future__ import annotations

import argparse
import os

from scripts.persist_fred_macro import _open_connection
from scripts.persist_fred_macro import load_local_env_if_available


def _fetch_all(connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    if hasattr(connection, "execute") and not hasattr(connection, "cursor"):
        result = connection.execute(sql, params)  # type: ignore[call-arg]
        rows = result.fetchall() if hasattr(result, "fetchall") else []
        return list(rows)
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        if not rows:
            return []
        columns = [desc[0] for desc in getattr(cursor, "description", [])]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        if hasattr(cursor, "close"):
            cursor.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect manual ingestion run history safely.")
    parser.add_argument("--vendor", default="polygon", help="Vendor filter, default polygon.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset filter, default ohlcv.")
    parser.add_argument("--limit", type=int, default=1, help="Maximum rows to print, default 1.")
    args = parser.parse_args()

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    connection = _open_connection(database_url)
    try:
        rows = _fetch_all(
            connection,
            """
            SELECT run_id, job_id, vendor, dataset, status, rows_fetched, rows_written, rows_rejected, error_count, started_at, finished_at
            FROM ingestion_runs
            WHERE vendor = %s AND dataset = %s
            ORDER BY finished_at DESC NULLS LAST, started_at DESC NULLS LAST
            LIMIT %s
            """.strip(),
            (args.vendor, args.dataset, args.limit),
        )
        for row in rows:
            print(
                f"run_id={row.get('run_id')} "
                f"job_id={row.get('job_id')} "
                f"vendor={row.get('vendor')} "
                f"dataset={row.get('dataset')} "
                f"status={row.get('status')} "
                f"rows_fetched={row.get('rows_fetched')} "
                f"rows_written={row.get('rows_written')} "
                f"rows_rejected={row.get('rows_rejected')} "
                f"error_count={row.get('error_count')} "
                f"started_at={row.get('started_at')} "
                f"finished_at={row.get('finished_at')}"
            )
        print(f"rows_returned={len(rows)}")
    finally:
        if hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
