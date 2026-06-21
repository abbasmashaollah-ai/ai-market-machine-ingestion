from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_quarantine_download_remaining_blocker_analysis.md")


def test_polygon_stock_day_agg_2026_06_16_quarantine_download_remaining_blocker_analysis_contains_required_language() -> None:
    assert DOC_PATH.exists(), "analysis doc must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Download implementation commit: `a02548b`",
        "Download approval package commit: `f03976a`",
        "Operator approval record commit: `3841b8f`",
        "Manual probe evidence commit: `89ca6da`",
        "Latest blocker evidence commit: `6fbc6e8`",
        "`config_classification: \"missing\"`",
        "`credentials_present: false`",
        "`download_attempted: false`",
        "`local_file_exists: false`",
        "`local_file_size_bytes: 0`",
        "`remote_listing_error_code_redacted: \"client_error\"`",
        "`remote_listing_error_message_redacted: \"remote listing failed safely\"`",
        "The blocker is the environment/config side of the generic downloader path",
        "Wrapper: not the blocker",
        "Generic downloader: not the direct blocker",
        "Adapter/environment: the remaining blocker",
        "Safety policy: intentionally still blocks unsafe download execution when config is missing",
        "one-date only",
        "exact approved phrase",
        "exact output path",
        "no parse",
        "no normalization",
        "no handoff/intake",
        "no DB write",
        "no data repo mutation",
        "no scheduler/backfill",
        "no AI wiring",
        "no secrets printed",
        "mocked remote object read/download path",
        "wrong phrase blocks",
        "missing phrase blocks",
        "correct phrase allows one-date quarantine write under mock",
        "output path exactly correct",
        "no parse/normalization/handoff/intake/DB/data repo/scheduler/backfill/AI flags",
        "Implement the smallest safe fix only if the environment is not already correctly configured",
        "Live vendor call/listing/probe",
        "Remote file read",
        "Download",
        "Quarantine write",
        "Parse/normalization/handoff/intake",
        "DB write",
        "Data repo mutation",
        "Scheduler/backfill",
        "AI wiring",
        "Generated output commit",
        "Unrelated untracked file staging/deletion",
        "Secrets printed",
        "the remaining blocker is environment/config presence for the download path",
    ]:
        assert phrase in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key=",
    ]:
        assert forbidden not in lowered
