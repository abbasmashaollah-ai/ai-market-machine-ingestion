from __future__ import annotations

from pathlib import Path
import unittest


class MacroRateObservationsContractDocTests(unittest.TestCase):
    def test_local_contract_doc_exists_and_mentions_required_fields(self) -> None:
        path = Path("docs/local_macro_rate_observations_contract.md")
        text = path.read_text(encoding="utf-8")

        self.assertIn("macro_rate_observations", text)
        self.assertIn("MacroRateObservation", text)
        self.assertIn("series_id + observation_date + source", text)
        self.assertIn("id` is database-managed", text)
        self.assertIn("FRED-Specific Source Rule", text)
        self.assertIn('source` for FRED observations should be', text)
