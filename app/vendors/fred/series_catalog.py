from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SeriesCategory(str, Enum):
    ECONOMIC_GROWTH = "economic_growth"
    INFLATION = "inflation"
    LABOR_MARKET = "labor_market"
    RATES_POLICY = "rates_policy"
    CONSUMER_BUSINESS_ACTIVITY = "consumer_business_activity"
    TRADE_GLOBAL_FLOWS = "trade_global_flows"
    FISCAL_GOVERNMENT = "fiscal_government"
    FINANCIAL_CONDITIONS = "financial_conditions"
    LIQUIDITY = "liquidity"


@dataclass(frozen=True)
class FREDSeriesDefinition:
    series_id: str
    name: str
    category: SeriesCategory
    frequency_hint: str | None
    units_hint: str | None
    priority: int
    active: bool = True


SERIES_CATALOG: tuple[FREDSeriesDefinition, ...] = (
    FREDSeriesDefinition("GDP", "Gross Domestic Product", SeriesCategory.ECONOMIC_GROWTH, "quarterly", "billions of dollars", 1),
    FREDSeriesDefinition("INDPRO", "Industrial Production Index", SeriesCategory.ECONOMIC_GROWTH, "monthly", "index", 2),
    FREDSeriesDefinition("RSAFS", "Retail Sales", SeriesCategory.CONSUMER_BUSINESS_ACTIVITY, "monthly", "millions of dollars", 3),
    FREDSeriesDefinition("CPIAUCSL", "Consumer Price Index for All Urban Consumers", SeriesCategory.INFLATION, "monthly", "index", 1),
    FREDSeriesDefinition("CPILFESL", "Core Consumer Price Index", SeriesCategory.INFLATION, "monthly", "index", 2),
    FREDSeriesDefinition("PPIACO", "Producer Price Index", SeriesCategory.INFLATION, "monthly", "index", 3),
    FREDSeriesDefinition("T10YIE", "10-Year Breakeven Inflation Rate", SeriesCategory.INFLATION, "daily", "percent", 4),
    FREDSeriesDefinition("UNRATE", "Unemployment Rate", SeriesCategory.LABOR_MARKET, "monthly", "percent", 1),
    FREDSeriesDefinition("PAYEMS", "Payroll Employment", SeriesCategory.LABOR_MARKET, "monthly", "thousands of persons", 2),
    FREDSeriesDefinition("CES0500000003", "Average Hourly Earnings", SeriesCategory.LABOR_MARKET, "monthly", "dollars", 3),
    FREDSeriesDefinition("JTSJOL", "Job Openings", SeriesCategory.LABOR_MARKET, "monthly", "thousands", 4),
    FREDSeriesDefinition("FEDFUNDS", "Effective Federal Funds Rate", SeriesCategory.RATES_POLICY, "monthly", "percent", 1),
    FREDSeriesDefinition("DGS10", "10-Year Treasury Constant Maturity Rate", SeriesCategory.RATES_POLICY, "daily", "percent", 2),
    FREDSeriesDefinition("DGS2", "2-Year Treasury Constant Maturity Rate", SeriesCategory.RATES_POLICY, "daily", "percent", 3),
    FREDSeriesDefinition("T10Y2Y", "10-Year Treasury Minus 2-Year Treasury", SeriesCategory.RATES_POLICY, "daily", "percent", 4),
    FREDSeriesDefinition("UMCSENT", "Consumer Sentiment", SeriesCategory.CONSUMER_BUSINESS_ACTIVITY, "monthly", "index", 1),
    FREDSeriesDefinition("HOUST", "Housing Starts", SeriesCategory.CONSUMER_BUSINESS_ACTIVITY, "monthly", "thousands", 2),
    FREDSeriesDefinition("BOPGSTB", "Trade Balance", SeriesCategory.TRADE_GLOBAL_FLOWS, "monthly", "billions of dollars", 1),
    FREDSeriesDefinition("M2SL", "M2 Money Stock", SeriesCategory.LIQUIDITY, "weekly", "billions of dollars", 1),
    FREDSeriesDefinition("BAMLH0A0HYM2", "ICE BofA High Yield Index", SeriesCategory.FINANCIAL_CONDITIONS, "daily", "percent", 1),
    FREDSeriesDefinition("TOTLL", "Total Loans and Leases", SeriesCategory.FINANCIAL_CONDITIONS, "weekly", "millions of dollars", 2),
)


def get_active_series() -> tuple[FREDSeriesDefinition, ...]:
    return tuple(series for series in SERIES_CATALOG if series.active)


def get_series_by_category(category: SeriesCategory | str) -> tuple[FREDSeriesDefinition, ...]:
    category_value = SeriesCategory(category)
    return tuple(series for series in SERIES_CATALOG if series.category == category_value)


def get_series_definition(series_id: str) -> FREDSeriesDefinition | None:
    normalized_series_id = series_id.strip().upper()
    for series in SERIES_CATALOG:
        if series.series_id.upper() == normalized_series_id:
            return series
    return None
