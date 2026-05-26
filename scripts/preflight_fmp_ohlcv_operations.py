from __future__ import annotations

from scripts.persist_fred_macro import _open_connection, load_local_env_if_available
from scripts.manual_ohlcv_preflight import run_preflight


def main() -> int:
    return run_preflight(vendor="fmp")


if __name__ == "__main__":
    raise SystemExit(main())
