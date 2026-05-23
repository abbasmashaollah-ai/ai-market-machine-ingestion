from __future__ import annotations

from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "docs" / "polygon_flatfile_official_layout_template.md"


def _status_value(template_text: str, key: str) -> str | None:
    prefix = f"{key}="
    for line in template_text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def main() -> int:
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    official_layout_captured = _status_value(template_text, "official_layout_captured") == "true"
    official_layout_verified = _status_value(template_text, "official_layout_verified") == "true"
    live_discovery_allowed = _status_value(template_text, "live_discovery_allowed") == "true"
    live_download_allowed = _status_value(template_text, "live_download_allowed") == "true"

    unsafe_state = bool((live_discovery_allowed or live_download_allowed) and not official_layout_verified)
    if not official_layout_captured:
        readiness_status = "layout_capture_pending"
    elif not official_layout_verified:
        readiness_status = "layout_captured_not_verified"
    else:
        readiness_status = "ready_for_mocked_discovery_tests"

    print(f"official_layout_captured={'true' if official_layout_captured else 'false'}")
    print(f"official_layout_verified={'true' if official_layout_verified else 'false'}")
    print(f"live_discovery_allowed={'true' if live_discovery_allowed else 'false'}")
    print(f"live_download_allowed={'true' if live_download_allowed else 'false'}")
    print(f"readiness_status={readiness_status}")
    print(f"unsafe_state={'true' if unsafe_state else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
