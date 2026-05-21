from __future__ import annotations

from app.models.normalized import NormalizedMacroObservation
from app.writers.canonical_writer import CanonicalWriter, WriterResult


class MacroWriter:
    writer_name = "macro_writer"

    def write(self, records: list[NormalizedMacroObservation]) -> WriterResult:
        raise NotImplementedError("Macro writer is not implemented yet.")


def build_macro_writer() -> CanonicalWriter:
    return MacroWriter()
