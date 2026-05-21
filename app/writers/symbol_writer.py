from __future__ import annotations

from app.models.normalized import NormalizedSymbolRecord
from app.writers.canonical_writer import CanonicalWriter, WriterResult


class SymbolWriter:
    writer_name = "symbol_writer"

    def write(self, records: list[NormalizedSymbolRecord]) -> WriterResult:
        raise NotImplementedError("Symbol writer is not implemented yet.")


def build_symbol_writer() -> CanonicalWriter:
    return SymbolWriter()
