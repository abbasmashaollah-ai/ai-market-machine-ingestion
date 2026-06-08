from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.preflight_polygon_flat_file_source_credentials as cli


def _run_with_env(monkeypatch, env: dict[str, str]) -> dict[str, object]:
    for name in cli.POLYGON_FLAT_FILE_CONFIG_NAMES + cli.AWS_GENERIC_CONFIG_NAMES:
        monkeypatch.delenv(name, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main([])
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def test_generic_aws_only_is_not_polygon_access(monkeypatch) -> None:
    payload = _run_with_env(
        monkeypatch,
        {
            "AWS_ACCESS_KEY_ID": "aws-key",
            "AWS_SECRET_ACCESS_KEY": "aws-secret",
            "AWS_DEFAULT_REGION": "us-west-2",
            "AWS_S3_BUCKET": "bucket",
            "AWS_S3_PREFIX": "prefix",
        },
    )
    assert payload["polygon_flat_file_config_present"] is False
    assert payload["generic_aws_s3_config_present"] is True
    assert payload["config_classification"] == "generic_aws_only"
    assert payload["credentials_printed"] is False


def test_polygon_config_is_classified_as_polygon_flat_file(monkeypatch) -> None:
    payload = _run_with_env(
        monkeypatch,
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://example.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "polygon-bucket",
            "POLYGON_FLAT_FILE_PREFIX": "polygon-prefix",
        },
    )
    assert payload["polygon_flat_file_config_present"] is True
    assert payload["generic_aws_s3_config_present"] is False
    assert payload["config_classification"] == "polygon_flat_file"
    assert payload["missing_polygon_config_names"] == []


def test_both_present_is_classified_correctly(monkeypatch) -> None:
    payload = _run_with_env(
        monkeypatch,
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://example.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "polygon-bucket",
            "POLYGON_FLAT_FILE_PREFIX": "polygon-prefix",
            "AWS_ACCESS_KEY_ID": "aws-key",
            "AWS_SECRET_ACCESS_KEY": "aws-secret",
            "AWS_DEFAULT_REGION": "us-west-2",
            "AWS_S3_BUCKET": "bucket",
            "AWS_S3_PREFIX": "prefix",
        },
    )
    assert payload["polygon_flat_file_config_present"] is True
    assert payload["generic_aws_s3_config_present"] is True
    assert payload["config_classification"] == "both_present"


def test_missing_state_is_classified_as_missing(monkeypatch) -> None:
    payload = _run_with_env(monkeypatch, {})
    assert payload["polygon_flat_file_config_present"] is False
    assert payload["generic_aws_s3_config_present"] is False
    assert payload["config_classification"] == "missing"
    assert payload["missing_polygon_config_names"] == list(cli.POLYGON_FLAT_FILE_CONFIG_NAMES)


def test_ambiguous_partial_configuration_is_classified_as_ambiguous(monkeypatch) -> None:
    payload = _run_with_env(
        monkeypatch,
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "AWS_ACCESS_KEY_ID": "aws-key",
        },
    )
    assert payload["config_classification"] == "ambiguous"
    assert payload["polygon_flat_file_config_present"] is False
    assert payload["generic_aws_s3_config_present"] is False


def test_output_never_prints_secret_or_endpoint_values(monkeypatch) -> None:
    payload = _run_with_env(
        monkeypatch,
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket-value",
            "POLYGON_FLAT_FILE_PREFIX": "prefix-value",
            "AWS_ACCESS_KEY_ID": "aws-key",
            "AWS_SECRET_ACCESS_KEY": "aws-secret",
            "AWS_DEFAULT_REGION": "us-west-2",
            "AWS_S3_BUCKET": "aws-bucket",
            "AWS_S3_PREFIX": "aws-prefix",
        },
    )
    text = json.dumps(payload, sort_keys=True).lower()
    for needle in ["polygon-key", "polygon-secret", "endpoint.invalid", "bucket-value", "prefix-value", "aws-key", "aws-secret", "us-west-2", "aws-bucket", "aws-prefix"]:
        assert needle not in text
    assert payload["credentials_printed"] is False
    assert payload["endpoint_value_printed"] is False
    assert payload["bucket_value_printed"] is False
    assert payload["prefix_value_printed"] is False


def test_output_includes_safe_blockers_and_next_step() -> None:
    payload = cli._safe_payload()
    assert isinstance(payload["blockers"], list)
    assert payload["next_allowed_step"]
    assert payload["production_handoff_generation_authorized"] is False
    assert payload["synthetic_forbidden"] is True
    assert payload["fixture_only_forbidden"] is True


def test_source_scan_blocks_vendor_calls_downloads_exports_db_writes_ingestion_scheduler_and_mutation() -> None:
    source_text = Path("scripts/preflight_polygon_flat_file_source_credentials.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source_text)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())
    for forbidden in ["requests", "httpx", "boto3", "sqlalchemy", "alembic", "app.api", "app.scheduler.jobs"]:
        assert forbidden not in import_names
    for phrase in [
        "vendor_call_attempted",
        "remote_bucket_list_attempted",
        "download_attempted",
        "export_attempted",
        "db_write_attempted",
        "ingestion_attempted",
        "scheduler_activation_attempted",
        "production_mutation_attempted",
        "production_handoff_generation_authorized",
        "synthetic_forbidden",
        "fixture_only_forbidden",
        "next_allowed_step",
    ]:
        assert phrase in source_text


def test_help_mentions_output_file_only() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_polygon_flat_file_source_credentials.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--output-file" in result.stdout
