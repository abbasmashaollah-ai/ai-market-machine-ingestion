from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch


def test_preflight_pass():
    import scripts.preflight_news_sentiment_operations as mod

    with patch("builtins.print") as print_mock:
        mod.main([])

    printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
    assert "dry_run_command_exists=True" in printed
    assert "source_plan_command_exists=True" in printed
    assert "foundation_doc_exists=True" in printed
    assert "source_plan_doc_exists=True" in printed
    assert "preflight_doc_exists=True" in printed
    assert "evidence_plan_doc_exists=True" in printed
    assert "normalization_module_exists=True" in printed
    assert "expected_fields_configured=True" in printed
    assert "no_database_url_required_yet=True" in printed
    assert "no_vendor_api_keys_required_yet=True" in printed
    assert "no_db_writes=True" in printed
    assert "forbidden_imports_absent=True" in printed


def test_no_forbidden_imports():
    text = Path("scripts/preflight_news_sentiment_operations.py").read_text(encoding="utf-8")
    lowered = text.lower()
    assert not re.search(r"^\s*import\s+fastapi\b", lowered, flags=re.MULTILINE)
    assert not re.search(r"^\s*from\s+fastapi\b", lowered, flags=re.MULTILINE)
    assert not re.search(r"^\s*import\s+requests\b", lowered, flags=re.MULTILINE)
    assert not re.search(r"^\s*from\s+requests\b", lowered, flags=re.MULTILINE)
    assert not re.search(r"^\s*import\s+httpx\b", lowered, flags=re.MULTILINE)
    assert not re.search(r"^\s*from\s+httpx\b", lowered, flags=re.MULTILINE)
    assert not re.search(r"^\s*import\s+alembic\b", lowered, flags=re.MULTILINE)
    assert not re.search(r"^\s*from\s+alembic\b", lowered, flags=re.MULTILINE)
    assert "import database_url" not in lowered
    assert "from database_url" not in lowered


def test_docs_coverage():
    preflight = Path("docs/news_sentiment_preflight.md").read_text(encoding="utf-8").lower()
    evidence = Path("docs/news_sentiment_evidence_plan.md").read_text(encoding="utf-8").lower()
    assert "news/sentiment preflight" in preflight
    assert "dry-run command exists" in preflight
    assert "source plan command exists" in preflight
    assert "foundation doc exists" in preflight
    assert "evidence plan doc exists" in preflight
    assert "the evidence plan remains deferred" in preflight
    assert "news/sentiment evidence plan" in evidence
    assert "row counts by `source`" in evidence
    assert "row counts by `ticker`" in evidence
    assert "missing title count" in evidence
    assert "missing published_at count" in evidence
    assert "missing url count" in evidence
    assert "missing sentiment label/score counts" in evidence
    assert "stale news checks" in evidence
    assert "no db reads yet" in evidence
    assert "no db writes yet" in evidence
