from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_producer_payload import build_market_feature_bundle_producer_payload
from app.writers.market_feature_bundle_writer import MarketFeatureBundleWriter


class FakeMarketFeatureBundleSession:
    def __init__(
        self,
        *,
        existing_by_idempotency_key: dict[str, object] | None = None,
        existing_by_grain: dict[tuple[object, object, object, object], object] | None = None,
        fail_on_commit: bool = False,
    ) -> None:
        self.added_payloads: list[dict[str, object]] = []
        self.merged_payloads: list[dict[str, object]] = []
        self.committed_count = 0
        self.rolled_back_count = 0
        self.fail_on_commit = fail_on_commit
        self._existing_by_idempotency_key = existing_by_idempotency_key or {}
        self._existing_by_grain = existing_by_grain or {}

    def existing_by_idempotency_key(self, key: str | None):
        return self._existing_by_idempotency_key.get(key) if key is not None else None

    def existing_by_grain(self, grain: dict[str, object]):
        key = (
            grain.get("observation_date"),
            grain.get("universe"),
            grain.get("schema_version"),
            grain.get("dataset_version"),
        )
        return self._existing_by_grain.get(key)

    def add(self, payload: dict[str, object]) -> None:
        self.added_payloads.append(deepcopy(payload))

    def merge(self, payload: dict[str, object]) -> None:
        self.merged_payloads.append(deepcopy(payload))

    def commit(self) -> None:
        if self.fail_on_commit:
            raise RuntimeError("commit failed")
        self.committed_count += 1

    def rollback(self) -> None:
        self.rolled_back_count += 1


def _payload() -> dict:
    bundle = run_market_feature_bundle_dry_run(observation_date="2026-01-15", timestamp="2026-01-15T12:00:00Z")
    return build_market_feature_bundle_producer_payload(
        bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )


def test_dry_run_valid_payload_returns_ready_and_does_not_mutate_session() -> None:
    session = FakeMarketFeatureBundleSession()
    writer = MarketFeatureBundleWriter(session, dry_run=True)
    payload = _payload()
    snapshot = deepcopy(payload)

    result = writer.write_payload(payload)

    assert result["write_status"] == "DRY_RUN_READY"
    assert result["would_write"] is True
    assert session.added_payloads == []
    assert session.committed_count == 0
    assert payload == snapshot


def test_missing_required_field_returns_rejected() -> None:
    session = FakeMarketFeatureBundleSession()
    writer = MarketFeatureBundleWriter(session, dry_run=True)
    payload = _payload()
    payload.pop("full_bundle_payload")

    result = writer.write_payload(payload)

    assert result["write_status"] == "REJECTED"
    assert result["would_write"] is False
    assert result["validation_errors"]


def test_invalid_source_repo_returns_rejected() -> None:
    session = FakeMarketFeatureBundleSession()
    writer = MarketFeatureBundleWriter(session, dry_run=True)
    payload = _payload()
    payload["source_repo"] = "wrong-repo"

    result = writer.write_payload(payload)

    assert result["write_status"] == "REJECTED"
    assert any(error["field_name"] == "source_repo" for error in result["validation_errors"])


def test_live_session_stub_writes_when_not_dry_run() -> None:
    session = FakeMarketFeatureBundleSession()
    writer = MarketFeatureBundleWriter(session, dry_run=False)

    result = writer.write_payload(_payload())

    assert result["write_status"] == "WRITE_ACCEPTED"
    assert result["would_write"] is True
    assert session.added_payloads
    assert session.committed_count == 1


def test_repeated_idempotency_key_returns_idempotent_noop() -> None:
    payload = _payload()
    session = FakeMarketFeatureBundleSession(existing_by_idempotency_key={payload["idempotency_key"]: {"idempotency_key": payload["idempotency_key"]}})
    writer = MarketFeatureBundleWriter(session, dry_run=False)

    result = writer.write_payload(payload)

    assert result["write_status"] == "IDEMPOTENT_NOOP"
    assert result["conflict_status"] == "ALREADY_EXISTS"
    assert session.committed_count == 0


def test_grain_conflict_returns_conflict_without_commit() -> None:
    payload = _payload()
    grain = (
        payload["observation_date"],
        payload["universe"],
        payload["schema_version"],
        payload["dataset_version"],
    )
    session = FakeMarketFeatureBundleSession(
        existing_by_grain={
            grain: {"idempotency_key": "other-key"},
        }
    )
    writer = MarketFeatureBundleWriter(session, dry_run=False)

    result = writer.write_payload(payload)

    assert result["write_status"] == "CONFLICT"
    assert result["conflict_status"] == "GRAIN_CONFLICT"
    assert session.committed_count == 0


def test_commit_failure_rolls_back_and_returns_failed() -> None:
    session = FakeMarketFeatureBundleSession(fail_on_commit=True)
    writer = MarketFeatureBundleWriter(session, dry_run=False)

    result = writer.write_payload(_payload())

    assert result["write_status"] == "WRITE_FAILED"
    assert session.rolled_back_count == 1


def test_writer_does_not_mutate_input_payload() -> None:
    session = FakeMarketFeatureBundleSession()
    writer = MarketFeatureBundleWriter(session, dry_run=True)
    payload = _payload()
    snapshot = deepcopy(payload)

    writer.write_payload(payload)

    assert payload == snapshot


def test_writer_source_has_no_forbidden_runtime_imports_or_terms() -> None:
    path = Path("app/writers/market_feature_bundle_writer.py")
    text = path.read_text(encoding="utf-8").lower()

    for marker in [
        "sqlalchemy",
        "app.database",
        "sessionlocal",
        "create_engine",
        "database_url",
        "requests",
        "httpx",
        "scheduler",
    ]:
        assert marker not in text

    for marker in [
        "ai judgment",
        "trading decision",
        "portfolio decision",
        "risk posture",
        "judge posture",
    ]:
        assert marker not in text

