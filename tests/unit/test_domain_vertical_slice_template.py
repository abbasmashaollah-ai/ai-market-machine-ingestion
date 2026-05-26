from __future__ import annotations

import unittest
from pathlib import Path


class DomainVerticalSliceTemplateTests(unittest.TestCase):
    def test_template_exists_and_has_required_sections(self) -> None:
        text = Path("docs/domain_vertical_slice_template.md").read_text(encoding="utf-8").lower()
        required_sections = (
            "domain purpose",
            "data repo dependency",
            "ingestion repo responsibilities",
            "vendor adapter",
            "normalization contract",
            "validation and quality checks",
            "writer/store boundary",
            "run-history recording",
            "quality-result recording",
            "lineage recording",
            "preflight command",
            "runner command",
            "evidence verifier",
            "required docs",
            "required tests",
            "forbidden imports and logic",
            "commit and push checklist",
        )
        for section in required_sections:
            self.assertIn(section, text)
