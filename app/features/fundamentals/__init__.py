"""Dry-run fundamentals feature slice."""

from .fundamentals_builder import build_fundamental_observation
from .fundamentals_engine import (
    calculate_balance_sheet_score,
    calculate_cash_flow_score,
    calculate_composite_fundamental_score,
    calculate_growth_score,
    calculate_profitability_score,
    calculate_valuation_score,
    determine_fundamental_quality_label,
)
from .fundamentals_job import FundamentalsDryRunResult, run_fundamentals_dry_run
from .fundamentals_report import build_fundamental_report
from .fundamentals_validator import (
    FundamentalValidationError,
    FundamentalValidationResult,
    validate_fundamental_observation,
    validate_fundamental_observations,
)
from .fundamentals_writer import FundamentalsMockWriter, FundamentalsWriterResult, write_fundamental_payloads

__all__ = [
    "FundamentalValidationError",
    "FundamentalValidationResult",
    "FundamentalsDryRunResult",
    "FundamentalsMockWriter",
    "FundamentalsWriterResult",
    "build_fundamental_observation",
    "build_fundamental_report",
    "calculate_balance_sheet_score",
    "calculate_cash_flow_score",
    "calculate_composite_fundamental_score",
    "calculate_growth_score",
    "calculate_profitability_score",
    "calculate_valuation_score",
    "determine_fundamental_quality_label",
    "run_fundamentals_dry_run",
    "validate_fundamental_observation",
    "validate_fundamental_observations",
    "write_fundamental_payloads",
]
