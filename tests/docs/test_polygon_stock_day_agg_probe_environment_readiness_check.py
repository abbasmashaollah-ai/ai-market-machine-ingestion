from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_probe_environment_readiness_check.md")


def test_polygon_stock_day_agg_probe_environment_readiness_check_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "readiness check doc must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Document the local readiness check required before retrying Polygon stock day aggregate vendor listing/probe.",
        "Verifies only dependency and config presence",
        "Does not call vendors",
        "Does not list vendor files",
        "Does not download vendor files",
        "Does not write files",
        "Does not create handoff outputs",
        "Does not create intake packages",
        "Does not print secrets or DB URLs",
        "`POLYGON_API_KEY`",
        "`POLYGON_FLAT_FILE_ACCESS_KEY_ID`",
        "`POLYGON_FLAT_FILE_SECRET_ACCESS_KEY`",
        "`POLYGON_FLAT_FILE_ENDPOINT`",
        "`POLYGON_FLAT_FILE_BUCKET`",
        "`POLYGON_FLAT_FILE_PREFIX`",
        "`boto3` availability",
        "Only safe type-level error reporting if import fails",
        "`boto3` available",
        "Required config keys present",
        "Operator approval record already exists",
        "Probe command remains listing-only",
        "No download flags are used",
        "Retry vendor listing/probe only",
        "Configure the missing dependency or config outside the repository, then rerun the readiness check.",
        "No scheduler activation",
        "No backfill",
        "No DB write",
        "No data repo mutation",
        "No AI wiring",
        "Unrelated untracked files untouched",
        "No secrets or DB URLs",
    ]:
        assert phrase in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key",
    ]:
        assert forbidden not in lowered
