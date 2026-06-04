from __future__ import annotations


def _row(symbol, implied_volatility_30d, implied_volatility_60d, realized_volatility_20d, iv_rank, iv_percentile, put_call_ratio, option_volume, call_volume, put_volume, open_interest, call_open_interest, put_open_interest, skew_25_delta, term_structure_slope, gamma_exposure=0.0):
    return {
        "symbol": symbol,
        "implied_volatility_30d": implied_volatility_30d,
        "implied_volatility_60d": implied_volatility_60d,
        "realized_volatility_20d": realized_volatility_20d,
        "iv_rank": iv_rank,
        "iv_percentile": iv_percentile,
        "put_call_ratio": put_call_ratio,
        "option_volume": option_volume,
        "call_volume": call_volume,
        "put_volume": put_volume,
        "open_interest": open_interest,
        "call_open_interest": call_open_interest,
        "put_open_interest": put_open_interest,
        "skew_25_delta": skew_25_delta,
        "term_structure_slope": term_structure_slope,
        "gamma_exposure": gamma_exposure,
    }


def build_options_metrics_scenario(name: str):
    if name == "high_volatility":
        return {
            "AAPL": _row("AAPL", 0.42, 0.45, 0.26, 82, 88, 1.3, 12000000, 5000000, 7000000, 30000000, 16000000, 14000000, -0.18, 0.12, 9000000),
            "MSFT": _row("MSFT", 0.39, 0.42, 0.24, 79, 84, 1.2, 11000000, 4800000, 6200000, 28000000, 15000000, 13000000, -0.15, 0.10, 7000000),
            "NVDA": _row("NVDA", 0.58, 0.62, 0.35, 95, 97, 1.6, 18000000, 6000000, 12000000, 42000000, 19000000, 23000000, -0.25, 0.18, 13000000),
        }
    if name == "low_volatility":
        return {
            "AAPL": _row("AAPL", 0.18, 0.20, 0.22, 18, 20, 0.85, 5000000, 2600000, 2400000, 12000000, 6500000, 5500000, -0.05, -0.08, 1000000),
            "MSFT": _row("MSFT", 0.16, 0.18, 0.20, 15, 18, 0.90, 4500000, 2300000, 2200000, 11000000, 6000000, 5000000, -0.04, -0.06, 800000),
            "NVDA": _row("NVDA", 0.22, 0.24, 0.25, 22, 25, 0.95, 5200000, 2700000, 2500000, 13000000, 7000000, 6000000, -0.06, -0.04, 900000),
        }
    if name == "skewed_protective":
        return {
            "AAPL": _row("AAPL", 0.31, 0.34, 0.24, 55, 60, 1.15, 8000000, 3400000, 4600000, 18000000, 8000000, 10000000, -0.22, 0.05, 5000000),
            "MSFT": _row("MSFT", 0.33, 0.35, 0.25, 58, 63, 1.20, 8200000, 3300000, 4900000, 19000000, 8500000, 10500000, -0.24, 0.06, 5200000),
            "NVDA": _row("NVDA", 0.40, 0.43, 0.28, 70, 76, 1.35, 10000000, 3800000, 6200000, 22000000, 9000000, 13000000, -0.30, 0.08, 6500000),
        }
    if name == "hedging_pressure":
        return {
            "AAPL": _row("AAPL", 0.34, 0.38, 0.24, 60, 66, 1.45, 9000000, 3500000, 5500000, 20000000, 9000000, 11000000, -0.20, 0.03, 6000000),
            "MSFT": _row("MSFT", 0.36, 0.40, 0.26, 62, 68, 1.50, 9300000, 3600000, 5700000, 21000000, 9500000, 11500000, -0.21, 0.02, 6200000),
            "NVDA": _row("NVDA", 0.45, 0.48, 0.30, 75, 80, 1.70, 12000000, 4200000, 7800000, 26000000, 11000000, 15000000, -0.28, 0.04, 8000000),
        }
    if name == "mixed_options":
        return {
            "AAPL": _row("AAPL", 0.26, 0.29, 0.24, 42, 45, 1.0, 7000000, 3500000, 3500000, 16000000, 8000000, 8000000, -0.12, 0.00, 3000000),
            "MSFT": _row("MSFT", 0.24, 0.27, 0.23, 40, 42, 1.05, 6800000, 3300000, 3500000, 15000000, 7600000, 7400000, -0.10, -0.01, 2500000),
            "NVDA": _row("NVDA", 0.31, 0.34, 0.29, 50, 52, 1.10, 8500000, 3600000, 4900000, 18000000, 8500000, 9500000, -0.18, 0.02, 4000000),
        }
    if name == "low_signal":
        return {
            "AAPL": _row("AAPL", 0.25, 0.25, 0.25, 0, 0, 1.0, 1000000, 500000, 500000, 5000000, 2500000, 2500000, 0.0, 0.0, 0.0),
        }
    raise ValueError(f"Unknown scenario: {name}")
