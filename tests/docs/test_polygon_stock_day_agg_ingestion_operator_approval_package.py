from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_ingestion_operator_approval_package.md")


def test_operator_approval_package_contains_required_language() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    required_phrases = [
        "This document is an approval package and does not execute anything.",
        "It does not grant ingestion production approval by itself.",
        "Production ingestion remains locked until a separate filled operator approval record exists.",
        "call vendors",
        "download files",
        "activate the scheduler",
        "mutate `ai-market-machine-data`",
        "write the database",
        "approve production automatically",
        "Gate 1: vendor credential readiness review",
        "Gate 2: tiny approved vendor listing probe approval",
        "Gate 3: tiny approved quarantine download approval",
        "Gate 4: local parse/normalization verification",
        "Gate 5: local handoff artifact generation approval",
        "Gate 6: data-repo intake descriptor generation approval",
        "Gate 7: handoff evidence package approval",
        "Gate 8: daily incremental job approval",
        "Gate 9: limited backfill approval",
        "Gate 10: scheduler activation approval",
        "clean git status, excluding expected local outputs if policy permits",
        "ingestion production readiness preflight output `READY_FOR_OPERATOR_REVIEW`",
        "required scripts, tests, and docs present",
        "no tracked generated artifacts",
        "vendor credential names configured but secret values not printed",
        "output directories confirmed local-only",
        "data repo mutation not attempted",
        "scheduler activation not attempted",
        "prior local artifact validation result",
        "intake descriptor validation result",
        "APPROVE POLYGON STOCK DAY AGG VENDOR LISTING PROBE",
        "APPROVE POLYGON STOCK DAY AGG QUARANTINE DOWNLOAD",
        "APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF GENERATION",
        "APPROVE POLYGON STOCK DAY AGG DATA REPO INTAKE DESCRIPTOR",
        "APPROVE POLYGON STOCK DAY AGG DAILY INCREMENTAL JOB",
        "APPROVE POLYGON STOCK DAY AGG LIMITED BACKFILL",
        "APPROVE POLYGON STOCK DAY AGG INGESTION SCHEDULER ACTIVATION",
        "vendor listing approval does not approve download",
        "download approval does not approve handoff generation",
        "handoff generation does not approve daily job",
        "daily job approval does not approve backfill",
        "backfill approval does not approve scheduler activation",
        "stop immediately on any vendor, auth, download, hash, parse, or validation mismatch",
        "Do not retry blindly.",
        "Preserve logs and local evidence.",
        "remove only local generated artifacts tied to the failed approved run",
        "Never mutate the data repo directly from ingestion.",
        "Never delete production warehouse data.",
        "call vendors",
        "download remote files",
        "write DB",
        "run migrations",
        "activate schedulers",
        "mutate `ai-market-machine-data`",
        "touch production",
        "print secrets",
        "Do not jump from vendor listing approval to download, or from backfill approval to scheduler activation.",
    ]

    for phrase in required_phrases:
        assert phrase in text

