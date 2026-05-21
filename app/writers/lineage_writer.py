from __future__ import annotations

from app.writers.canonical_writer import CanonicalWriter, WriterResult


class LineageWriter:
    writer_name = "lineage_writer"

    def write(self, records: list[object]) -> WriterResult:
        raise NotImplementedError("Lineage writer is not implemented yet.")


def build_lineage_writer() -> CanonicalWriter:
    return LineageWriter()
