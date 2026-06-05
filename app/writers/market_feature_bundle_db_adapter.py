from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse, urlunparse

from sqlalchemy import Integer, JSON, Column, MetaData, String, Table, create_engine, delete, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

TARGET_TABLE = "market_feature_bundle_snapshots"
ALLOW_UNSAFE_ENV = "AMM_ALLOW_UNSAFE_TEST_DB_WRITES"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_from_payload(payload: dict[str, object]) -> dict[str, object]:
    row = dict(payload)
    generated_at = row.get("generated_at")
    if generated_at is None or (isinstance(generated_at, str) and not generated_at.strip()):
        row["generated_at"] = _utc_now_iso()
    return row


def redact_database_url(database_url: str) -> str:
    parsed = urlparse(database_url)
    netloc = parsed.netloc
    if "@" in netloc:
        creds, host = netloc.rsplit("@", 1)
        if ":" in creds:
            username, _ = creds.split(":", 1)
            netloc = f"{username}:<redacted>@{host}"
        else:
            netloc = f"<redacted>@{host}"
    redacted = parsed._replace(netloc=netloc)
    return urlunparse(redacted)


def _is_unsafe_hostname(hostname: str | None) -> bool:
    if not hostname:
        return True
    lower = hostname.lower()
    unsafe_tokens = ("prod", "production", "railway", "aws", "rds", "cloudsql")
    return any(token in lower for token in unsafe_tokens)


def validate_safe_test_database_url(database_url: str) -> None:
    if not database_url or not database_url.strip():
        raise ValueError("safe test database URL is required")
    parsed = urlparse(database_url)
    hostname = parsed.hostname
    if _is_unsafe_hostname(hostname) and os.getenv(ALLOW_UNSAFE_ENV, "").strip() != "YES_I_UNDERSTAND":
        raise ValueError(f"unsafe test database URL rejected: {redact_database_url(database_url)}")


def create_safe_test_engine(database_url: str) -> Engine:
    validate_safe_test_database_url(database_url)
    return create_engine(database_url, future=True)


def build_market_feature_bundle_table(metadata: MetaData) -> Table:
    return Table(
        TARGET_TABLE,
        metadata,
        Column("observation_date", String, nullable=False),
        Column("generated_at", String, nullable=False),
        Column("universe", String, nullable=False),
        Column("schema_version", String, nullable=False),
        Column("dataset_version", String, nullable=False),
        Column("idempotency_key", String, nullable=False),
        Column("raw_sections", JSON, nullable=False),
        Column("synthesized_sections", JSON, nullable=False),
        Column("section_record_counts", JSON, nullable=False),
        Column("section_labels", JSON, nullable=False),
        Column("compact_summary", JSON, nullable=False),
        Column("full_bundle_payload", JSON, nullable=False),
        Column("validation_status", String, nullable=False),
        Column("validation_errors", JSON, nullable=False),
        Column("validation_warnings", JSON, nullable=False),
        Column("total_warnings", Integer, nullable=False),
        Column("safety_flags", JSON, nullable=False),
        Column("rejected_counts", JSON, nullable=False),
        Column("certification_status", String, nullable=False),
        Column("source_repo", String, nullable=False),
        Column("source_run_id", String, nullable=True),
        Column("input_dataset_versions", JSON, nullable=False),
        Column("lineage_refs", JSON, nullable=False),
        Column("quality_result_refs", JSON, nullable=False),
    )


@dataclass
class MarketFeatureBundleSqlAlchemySessionAdapter:
    engine: Engine
    table: Table
    _staged_rows: list[dict[str, object]] = field(default_factory=list)
    _committed_rows: list[dict[str, object]] = field(default_factory=list)

    def existing_by_idempotency_key(self, key: str | None):
        if not key:
            return None
        with self.engine.connect() as connection:
            row = connection.execute(select(self.table).where(self.table.c.idempotency_key == key)).mappings().first()
            return dict(row) if row else None

    def existing_by_grain(self, grain: dict[str, object]):
        with self.engine.connect() as connection:
            row = connection.execute(
                select(self.table).where(
                    self.table.c.observation_date == grain.get("observation_date"),
                    self.table.c.universe == grain.get("universe"),
                    self.table.c.schema_version == grain.get("schema_version"),
                    self.table.c.dataset_version == grain.get("dataset_version"),
                )
            ).mappings().first()
            return dict(row) if row else None

    def add(self, payload: dict[str, object]) -> None:
        self._staged_rows.append(_row_from_payload(payload))

    def merge(self, payload: dict[str, object]) -> None:
        self._staged_rows.append(_row_from_payload(payload))

    def commit(self) -> None:
        if not self._staged_rows:
            return
        with self.engine.begin() as connection:
            for payload in self._staged_rows:
                existing = connection.execute(
                    select(self.table.c.idempotency_key).where(self.table.c.idempotency_key == payload["idempotency_key"])
                ).first()
                if existing is not None:
                    continue
                conflict = connection.execute(
                    select(self.table.c.idempotency_key).where(
                        self.table.c.observation_date == payload["observation_date"],
                        self.table.c.universe == payload["universe"],
                        self.table.c.schema_version == payload["schema_version"],
                        self.table.c.dataset_version == payload["dataset_version"],
                    )
                ).first()
                if conflict is not None and conflict[0] != payload["idempotency_key"]:
                    continue
                connection.execute(insert(self.table).values(**payload))
                self._committed_rows.append(dict(payload))
        self._staged_rows.clear()

    def rollback(self) -> None:
        self._staged_rows.clear()

    def cleanup_by_idempotency_key(self, idempotency_key: str) -> int:
        with self.engine.begin() as connection:
            result = connection.execute(delete(self.table).where(self.table.c.idempotency_key == idempotency_key))
            return int(result.rowcount or 0)


def build_market_feature_bundle_session(database_url: str) -> MarketFeatureBundleSqlAlchemySessionAdapter:
    engine = create_safe_test_engine(database_url)
    metadata = MetaData()
    table = build_market_feature_bundle_table(metadata)
    return MarketFeatureBundleSqlAlchemySessionAdapter(engine=engine, table=table)
