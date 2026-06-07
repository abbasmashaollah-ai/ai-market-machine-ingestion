from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

from tests.fixtures.market_feature_bundle.fixture_validator import validate_fixture_file


FIXTURE_DIR = Path("tests/fixtures/market_feature_bundle")


def _load_module_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def test_market_feature_bundle_multi_symbol_fixture_payloads_validate() -> None:
    for name in ["qqq", "iwm", "dia"]:
        path = FIXTURE_DIR / f"{name}_fixture_dry_run.json"
        assert path.exists()
        assert validate_fixture_file(path) == []


def test_market_feature_bundle_multi_symbol_fixture_payloads_contract_and_safety() -> None:
    for name in ["qqq", "iwm", "dia"]:
        path = FIXTURE_DIR / f"{name}_fixture_dry_run.json"
        text = path.read_text(encoding="utf-8").lower()
        payload_module_text = _load_module_text(FIXTURE_DIR / "fixture_validator.py")
        assert validate_fixture_file(path) == []

        for needle in [
            f'"universe": "{name}"',
            '"observation_date": "2026-01-15"',
            '"schema_version": "market_feature_bundle.v1"',
            '"dataset_version": "production_pilot.fixture_dry_run.v1"',
            '"validation_status": "pass"',
            '"coverage_status": "complete"',
            '"quality_status": "pass"',
            '"source_repo": "ai-market-machine-ingestion"',
            '"source_run_id": "fixture_dry_run.v1"',
            "fixture-only dry-run payload and not production evidence",
            "lineage_refs",
            "quality_result_refs",
            "raw_sections",
            "synthesized_sections",
            "compact_summary",
            "full_bundle_payload",
            "validation_errors",
            "validation_warnings",
            "idempotency_key",
        ]:
            assert needle in text

        assert '"certification_status": "fixture_certified"' in text or '"certification_status": "dry_run_certified"' in text
        assert '"certification_status": "certified"' not in text
        assert "secret" not in text
        assert "token" not in text
        assert "credential" not in text
        assert "raw_provider" not in text

        for forbidden in [
            "data api",
            "production route",
            "sqlalchemy",
            "session",
            "engine",
            "vendor",
            "scheduler",
            "writer",
        ]:
            assert forbidden not in payload_module_text


def test_market_feature_bundle_fixture_validator_module_has_no_runtime_imports() -> None:
    path = FIXTURE_DIR / "fixture_validator.py"
    source = path.read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())

    for forbidden in [
        "requests",
        "httpx",
        "sqlalchemy",
        "scheduler",
        "vendor",
        "engine",
        "session",
        "writer",
        "app.writers",
        "app.features",
    ]:
        assert forbidden not in import_names
