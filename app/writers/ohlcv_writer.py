from __future__ import annotations

from app.models.normalized import NormalizedOHLCVRecord
from app.writers.canonical_writer import CanonicalWriter, WriteStatus, WriterResult


class OhlcvWriter:
    writer_name = "ohlcv_writer"

    def write(self, records: list[NormalizedOHLCVRecord]) -> WriterResult:
        raise NotImplementedError("OHLCV writer is not implemented yet.")


def build_ohlcv_writer() -> CanonicalWriter:
    return OhlcvWriter()
