from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileOfficialLayoutCaptureTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_flatfile_official_layout_capture as mod

        return mod

    def test_layout_capture_pending_by_default(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("official_layout_captured=false", printed)
        self.assertIn("official_layout_verified=false", printed)
        self.assertIn("live_discovery_allowed=false", printed)
        self.assertIn("live_download_allowed=false", printed)
        self.assertIn("readiness_status=layout_capture_pending", printed)
        self.assertIn("unsafe_state=false", printed)

    def test_unsafe_state_when_live_flags_true_and_unverified(self) -> None:
        mod = self._module()
        template = """official_layout_captured=true
official_layout_verified=false
live_discovery_allowed=true
live_download_allowed=true
"""
        fake_path = type("FakePath", (), {"read_text": lambda self, encoding="utf-8": template})()
        with patch.object(mod, "TEMPLATE_PATH", fake_path), patch("builtins.print") as print_mock:
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("official_layout_captured=true", printed)
        self.assertIn("official_layout_verified=false", printed)
        self.assertIn("unsafe_state=true", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_official_layout_capture.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("S3", text)
        self.assertNotIn("requests", text)
