from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import scripts.build_polygon_stock_day_agg_data_repo_intake_package as cli


MANIFEST = Path("outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-15_2026-06-15_manifest.json")


def _run_cli(argv: list[str]) -> dict[str, object]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(argv)
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def test_valid_manifest_writes_package_descriptor(tmp_path) -> None:
    output_dir = Path("outputs") / "intake_packages" / "polygon_stock_day_aggs"
    payload = _run_cli(
        [
            "--manifest",
            str(MANIFEST),
            "--output-dir",
            str(output_dir),
            "--package-id",
            "polygon_stock_day_aggs_2026-06-15_2026-06-15",
        ]
    )
    package_path = Path(payload["intake_package_path"])
    assert payload["intake_package_written"] is True
    assert payload["validation_passed"] is True
    assert package_path.exists()
    package = json.loads(package_path.read_text(encoding="utf-8"))
    assert package["package_type"] == "data_repo_intake_descriptor"
    assert package["dataset"] == "ohlcv_equity_daily"
    assert package["source_vendor"] == "polygon_massive_flat_files"
    assert package["source_dataset"] == "polygon_stocks_day_aggs"
    assert package["preview_or_local_handoff_only"] is True
    assert package["db_write_authorized"] is False
    assert package["data_repo_mutation_authorized"] is False


def test_invalid_manifest_writes_nothing(tmp_path) -> None:
    manifest_path = tmp_path / "missing.json"
    output_dir = tmp_path / "blocked" / "polygon_stock_day_aggs"
    payload = _run_cli(["--manifest", str(manifest_path), "--output-dir", str(output_dir)])
    assert payload["validation_passed"] is False
    assert payload["intake_package_written"] is False
    assert not Path(payload["intake_package_path"]).exists()


def test_output_dir_outside_approved_root_is_refused(tmp_path) -> None:
    payload = _run_cli(
        [
            "--manifest",
            str(MANIFEST),
            "--output-dir",
            str(tmp_path / "not_allowed"),
        ]
    )
    assert payload["intake_package_written"] is False
    assert "output_dir must be within" in payload["blockers"][-1]
