from __future__ import annotations

from app.core.health import check_runtime_health


def main() -> int:
    status = check_runtime_health()
    print(status.to_dict())
    print("railway-start: idle placeholder, ingestion disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
