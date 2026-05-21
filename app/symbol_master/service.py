from __future__ import annotations

from typing import Protocol

from app.models.normalized import NormalizedSymbolRecord


class SymbolMasterService(Protocol):
    def resolve(self, symbol: str, vendor: str | None = None) -> NormalizedSymbolRecord:
        ...

    def sync(self) -> None:
        ...

    def update(self, record: NormalizedSymbolRecord) -> None:
        ...


class UnsupportedSymbolMasterService:
    def resolve(self, symbol: str, vendor: str | None = None) -> NormalizedSymbolRecord:
        raise NotImplementedError("Symbol master service is not implemented yet.")

    def sync(self) -> None:
        raise NotImplementedError("Symbol master service is not implemented yet.")

    def update(self, record: NormalizedSymbolRecord) -> None:
        raise NotImplementedError("Symbol master service is not implemented yet.")
