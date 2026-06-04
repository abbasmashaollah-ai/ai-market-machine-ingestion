from __future__ import annotations

from pathlib import Path


FORBIDDEN_MARKERS = (
    "sqlalchemy",
    "create_engine",
    "sessionlocal",
    "get_db",
    "database_url",
    "psycopg2",
    "requests",
    "httpx",
    "aiohttp",
    "apscheduler",
    "open db session",
)


def _feature_python_files() -> list[Path]:
    root = Path("app/features")
    return [
        path
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def test_app_features_remain_calculation_only() -> None:
    for path in _feature_python_files():
        text = path.read_text(encoding="utf-8").lower()
        if path.name == "market_feature_bundle_mock_writer.py":
            continue
        for marker in FORBIDDEN_MARKERS:
            assert marker not in text, f"{path} contains forbidden marker: {marker}"


def test_app_features_do_not_import_market_feature_bundle_db_adapter() -> None:
    for path in _feature_python_files():
        text = path.read_text(encoding="utf-8").lower()
        assert "market_feature_bundle_db_adapter" not in text, f"{path} imports the db adapter"


def test_market_feature_bundle_mock_writer_stays_mock_only() -> None:
    path = Path("app/features/market_features/market_feature_bundle_mock_writer.py")
    text = path.read_text(encoding="utf-8").lower()

    for marker in [
        "sqlalchemy",
        "sessionlocal",
        "get_db",
        "database_url",
        "requests",
        "httpx",
        "commit(",
        "execute(",
    ]:
        assert marker not in text, f"{path} contains forbidden marker: {marker}"

    for marker in [
        "dry_run_only",
        "mock",
    ]:
        assert marker in text

    assert "featuresnapshot" not in text
    assert "marketsnapshot" not in text
