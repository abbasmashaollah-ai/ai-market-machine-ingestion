from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from app.features.breadth.breadth_builder import build_breadth_observation
from app.features.breadth.breadth_jsonl_handoff_builder import (
    DEFAULT_SCHEMA_VERSION,
    build_breadth_observations_handoff_records,
    read_breadth_observations_handoff_jsonl,
    validate_breadth_observation_handoff_record,
    write_breadth_observations_handoff_jsonl,
)
from tests.fixtures.breadth_ohlcv import build_breadth_ohlcv_fixtures


def _observation() -> dict[str, object]:
    fixtures = build_breadth_ohlcv_fixtures()
    volume_histories = {symbol: [{"volume": row["volume"]} for row in history] for symbol, history in fixtures.items()}
    observation = build_breadth_observation("SP500", fixtures, volume_histories, "2026-01-15")
    observation["source"] = "fixture_vendor"
    observation["source_dataset"] = "breadth_observations"
    observation["source_sha256"] = "fixture-source-sha256"
    observation["source_file"] = "fixtures/breadth/breadth.jsonl"
    observation["source_uri"] = "file:///fixtures/breadth/breadth.jsonl"
    observation["universe_name"] = "S&P 500"
    return observation


def _expected_idempotency_key() -> str:
    digest = sha256()
    for part in (
        "fixture_vendor",
        "breadth_observations",
        "fixture-source-sha256",
        "2026-01-15",
        "SP500",
        "breadth_observations_jsonl_v1",
    ):
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def test_builder_maps_universe_to_universe_key_and_excludes_derived_top_level_fields(tmp_path: Path) -> None:
    result = write_breadth_observations_handoff_jsonl(
        [_observation()],
        tmp_path / "breadth.jsonl",
        source_vendor="fixture_vendor",
        source_dataset="breadth_observations",
        source_sha256="fixture-source-sha256",
        generated_at="2026-01-15T16:00:00Z",
    )

    assert result.records_received == 1
    assert result.records_written == 1
    assert result.records_rejected == 0
    assert result.no_vendor_calls is True
    assert result.no_db_writes is True
    assert result.output_path.endswith("breadth.jsonl")
    assert result.idempotency_keys
    assert result.lineage_summary["schema_version"] == DEFAULT_SCHEMA_VERSION

    records = read_breadth_observations_handoff_jsonl(result.output_path)
    assert len(records) == 1
    record = records[0]
    assert record["universe_key"] == "SP500"
    assert record["universe_name"] == "S&P 500"
    assert "universe" not in record
    assert record["source_vendor"] == "fixture_vendor"
    assert record["source_dataset"] == "breadth_observations"
    assert record["source_sha256"] == "fixture-source-sha256"
    assert record["observed_symbol_count"] == record["advancing_count"] + record["declining_count"] + record["unchanged_count"]
    assert record["schema_version"] == DEFAULT_SCHEMA_VERSION
    assert record["metadata"]["trace"]["advance_decline_line"] == _observation()["advance_decline_line"]
    assert "advance_decline_line" not in record
    assert "breadth_score" not in record
    assert "participation_score" not in record
    assert "participation_label" not in record


def test_builder_idempotency_key_is_deterministic_and_uses_expected_formula() -> None:
    record = _observation()
    result = build_breadth_observations_handoff_records(
        [record],
        source_vendor="fixture_vendor",
        source_dataset="breadth_observations",
        source_sha256="fixture-source-sha256",
        generated_at="2026-01-15T16:00:00Z",
    )[0]

    assert result.accepted is True
    assert result.idempotency_key is not None
    assert result.idempotency_key == _expected_idempotency_key()

    mutated = dict(record)
    mutated["source_sha256"] = "different"
    other = build_breadth_observations_handoff_records(
        [mutated],
        source_vendor="fixture_vendor",
        source_dataset="breadth_observations",
        source_sha256="fixture-source-sha256",
        generated_at="2026-01-15T16:00:00Z",
    )[0]
    assert other.idempotency_key != result.idempotency_key


def test_builder_rejects_invalid_rows_and_writes_quarantine(tmp_path: Path) -> None:
    valid = _observation()
    invalid = dict(valid)
    invalid["advancing_count"] = -1
    invalid["metadata"] = {"trace": {"advance_decline_line": 1}}

    result = write_breadth_observations_handoff_jsonl(
        [valid, invalid],
        tmp_path / "breadth.jsonl",
        source_vendor="fixture_vendor",
        source_dataset="breadth_observations",
        source_sha256="fixture-source-sha256",
        quarantine_path=tmp_path / "quarantine.jsonl",
    )

    assert result.records_received == 2
    assert result.records_written == 1
    assert result.records_rejected == 1
    assert result.quarantine_path is not None
    quarantine = Path(result.quarantine_path)
    assert quarantine.exists()
    quarantined = quarantine.read_text(encoding="utf-8").strip().splitlines()
    assert len(quarantined) == 1
    quarantined_record = json.loads(quarantined[0])
    assert quarantined_record["index"] == 1
    assert quarantined_record["rejection_reasons"]
    assert result.lineage_summary["source_vendor"] == "fixture_vendor"
    assert result.lineage_summary["source_dataset"] == "breadth_observations"


def test_validation_requires_universe_key_and_lineage_fields() -> None:
    observation = _observation()
    record = {
        "observation_date": observation["observation_date"],
        "source_vendor": "fixture_vendor",
        "source_dataset": "breadth_observations",
        "source_sha256": "fixture-source-sha256",
        "observed_symbol_count": 1,
        "advancing_count": 1,
        "declining_count": 0,
        "unchanged_count": 0,
        "advancing_volume": 1.0,
        "declining_volume": 0.0,
        "new_high_count": 0,
        "new_low_count": 0,
        "generated_at": "2026-01-15T16:00:00Z",
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "metadata": {},
    }
    result = validate_breadth_observation_handoff_record(record)
    assert result.accepted is False
    assert any("universe_key" in reason for reason in result.rejection_reasons)
