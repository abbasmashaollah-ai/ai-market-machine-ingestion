from __future__ import annotations

from pathlib import Path


EXECUTABLE_ROOTS = ("app", "scripts")

FORBIDDEN_MARKERS = (
    "FastAPI",
    "APIRouter",
    "alembic",
    "Base.metadata.create_all",
    "from ai_market_machine_data",
    "import ai_market_machine_data",
)


def _iter_python_files(repo_root: Path):
    for root_name in EXECUTABLE_ROOTS:
        yield from (path for path in (repo_root / root_name).rglob("*.py") if path.is_file())


def test_active_code_has_no_public_api_or_schema_owner_markers():
    repo_root = Path(__file__).resolve().parents[2]
    violations: list[str] = []

    for path in _iter_python_files(repo_root):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                violations.append(f"{path}:{marker}")

    assert violations == [], f"forbidden boundary markers remain in active code: {violations}"
