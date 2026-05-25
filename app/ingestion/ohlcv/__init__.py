"""Single-symbol OHLCV ingestion slice for ai-market-machine-ingestion."""

from app.ingestion.ohlcv.fanout import (
    FmpMultiSymbolOhlcvFanoutRequest,
    FmpMultiSymbolOhlcvFanoutResult,
    build_multi_symbol_ohlcv_fanout,
)
from app.ingestion.ohlcv.normalization import normalize_fmp_ohlcv_record, normalize_fmp_ohlcv_records
from app.ingestion.ohlcv.orchestrator import (
    FmpOhlcvIngestionPlan,
    FmpOhlcvIngestionRequest,
    build_single_symbol_ohlcv_write_plan,
)

__all__ = [
    "FmpMultiSymbolOhlcvFanoutRequest",
    "FmpMultiSymbolOhlcvFanoutResult",
    "FmpOhlcvIngestionPlan",
    "FmpOhlcvIngestionRequest",
    "build_multi_symbol_ohlcv_fanout",
    "build_single_symbol_ohlcv_write_plan",
    "normalize_fmp_ohlcv_record",
    "normalize_fmp_ohlcv_records",
]
