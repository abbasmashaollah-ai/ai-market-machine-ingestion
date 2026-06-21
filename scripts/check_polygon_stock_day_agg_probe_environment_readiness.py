from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.vendors.polygon_stock_day_agg_probe_environment_readiness import render_probe_environment_readiness_json


def main() -> int:
    sys.stdout.write(render_probe_environment_readiness_json())
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
