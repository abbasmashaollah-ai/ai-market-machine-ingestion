from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_production_seed_dry_run_checkpoint_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_production_seed_dry_run_checkpoint.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "successful multi-symbol production seed scaffold dry-run",
        "qqq/iwm/dia are production candidates",
        "--symbols qqq,iwm,dia",
        "--observation-date 2026-01-15",
        "--dataset-version production_pilot.v1",
        "multi_symbol_production_seed_dry_run_output.json",
        "dry_run true",
        "execute_requested false",
        "db_write_attempted false",
        "db_write_allowed false",
        "production_write_attempted false",
        "production_writer_untouched true",
        "source_scan_safe true",
        "safe_summary_only true",
        "approval_env_present false",
        "db_url_env_present false",
        "symbols_requested qqq/iwm/dia",
        "symbols_ready qqq/iwm/dia",
        "symbols_blocked empty",
        "invalid_symbols empty",
        "validation_status pass",
        "coverage_status complete",
        "quality_status pass",
        "certification_status production_candidate",
        "schema_version market_feature_bundle.v1",
        "dataset_version production_pilot.v1",
        "observation_date 2026-01-15",
        "per-symbol ready for qqq/iwm/dia",
        "lineage_refs_present true",
        "quality_result_refs_present true",
        "idempotency_key_prefix only",
        "not a production seed/write",
        "not data api certification",
        "not production evidence",
        "not ai machine multi-symbol readiness yet",
        "not approval to execute db write",
        "explicit second approval before implementing or executing db write path",
        "data api verification after any approved write",
        "ai machine multi-symbol diagnostic remains blocked until data api shows qqq/iwm/dia certified",
        "no production seed/write",
        "no db writes",
        "no vendor calls",
        "no live api calls",
        "no scheduler activation",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
    ]:
        assert needle in text

