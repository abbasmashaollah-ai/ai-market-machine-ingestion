from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_vendor_probe_environment_readiness_design.md")


def test_polygon_stock_day_agg_vendor_probe_environment_readiness_design_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "environment readiness design must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Define environment requirements before retrying Polygon stock day aggregate vendor listing/probe.",
        "Probe utility exists",
        "Safe-block behavior worked",
        "Remote listing was not executed",
        "Missing Polygon flat-file config",
        "Missing `boto3` dependency",
        "Required non-secret config keys/names must be present",
        "Required AWS/S3/Polygon flat-file credential/config presence must be verified without exposing secrets",
        "`boto3` dependency must be available",
        "Command must remain listing/probe-only",
        "No download",
        "No file write",
        "No quarantine write",
        "No parse/normalization/handoff",
        "Do not print credentials",
        "Do not commit credentials",
        "Do not include DB URLs",
        "Do not store API keys, tokens, or passwords in docs",
        "Only document presence or absence of required config by key name, never values",
        "`boto3` available",
        "Required config present",
        "Operator approval record already exists",
        "Probe command uses listing-only mode",
        "Output/evidence captures availability and metadata only",
        "No download flags used",
        "python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-15 --end-date 2026-06-15 --max-days 1",
        "Do not add download, write, parse, or handoff flags.",
        "If config or dependency is still missing, block again and record evidence",
        "If vendor denies access, record availability/access evidence but do not retry with broader permissions",
        "If multiple files are found, do not download; create a separate download approval package",
        "Create an environment readiness approval/check package or run a safe dependency/config presence check.",
        "No vendor call/listing/probe in this design",
        "No package install",
        "No code/script modification",
        "No scheduler/backfill",
        "No DB write",
        "No data repo mutation",
        "No AI wiring",
        "No generated output commit",
        "Unrelated untracked files untouched",
        "No secrets or DB URLs",
    ]:
        assert phrase in text

    assert "e16402c" in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
    ]:
        assert forbidden not in lowered
