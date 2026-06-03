from __future__ import annotations


def _payload(etf_flows, options_positioning, futures_positioning, short_interest, fund_exposure):
    return {
        "etf_flows": etf_flows,
        "options_positioning": options_positioning,
        "futures_positioning": futures_positioning,
        "short_interest": short_interest,
        "fund_exposure": fund_exposure,
    }


def build_flows_positioning_payload_scenario(name: str):
    if name == "risk_on_flows":
        return _payload(
            [
                {"symbol": "SPY", "flow_1d": 1200000000, "flow_5d": 4200000000, "flow_20d": 10000000000, "aum": 500000000000},
                {"symbol": "QQQ", "flow_1d": 900000000, "flow_5d": 3200000000, "flow_20d": 8500000000, "aum": 300000000000},
                {"symbol": "XLP", "flow_1d": -150000000, "flow_5d": -300000000, "flow_20d": -500000000, "aum": 25000000000},
                {"symbol": "HYG", "flow_1d": 300000000, "flow_5d": 900000000, "flow_20d": 2500000000, "aum": 20000000000},
            ],
            {"put_call_ratio": 0.7, "equity_put_call_ratio": 0.8, "index_put_call_ratio": 0.75, "call_volume": 12000000, "put_volume": 8000000},
            [{"asset": "ES", "net_spec_position": 250000, "net_position_percentile": 0.8}, {"asset": "NQ", "net_spec_position": 180000, "net_position_percentile": 0.75}],
            [{"symbol": "TSLA", "short_interest_percent_float": 0.05, "days_to_cover": 1.2}, {"symbol": "NVDA", "short_interest_percent_float": 0.03, "days_to_cover": 0.8}],
            {"gross_exposure": 1.6, "net_exposure": 0.8, "cash_level": 0.05},
        )
    if name == "risk_off_flows":
        return _payload(
            [
                {"symbol": "SPY", "flow_1d": -1500000000, "flow_5d": -5200000000, "flow_20d": -11000000000, "aum": 500000000000},
                {"symbol": "QQQ", "flow_1d": -900000000, "flow_5d": -3300000000, "flow_20d": -7600000000, "aum": 300000000000},
                {"symbol": "XLP", "flow_1d": 200000000, "flow_5d": 500000000, "flow_20d": 900000000, "aum": 25000000000},
                {"symbol": "HYG", "flow_1d": -400000000, "flow_5d": -1100000000, "flow_20d": -2600000000, "aum": 20000000000},
            ],
            {"put_call_ratio": 1.4, "equity_put_call_ratio": 1.5, "index_put_call_ratio": 1.45, "call_volume": 7000000, "put_volume": 14000000},
            [{"asset": "ES", "net_spec_position": -220000, "net_position_percentile": 0.2}, {"asset": "NQ", "net_spec_position": -140000, "net_position_percentile": 0.25}],
            [{"symbol": "TSLA", "short_interest_percent_float": 0.18, "days_to_cover": 4.8}, {"symbol": "NVDA", "short_interest_percent_float": 0.12, "days_to_cover": 3.5}],
            {"gross_exposure": 0.9, "net_exposure": -0.4, "cash_level": 0.25},
        )
    if name == "crowded_long":
        return _payload(
            [
                {"symbol": "SPY", "flow_1d": 1800000000, "flow_5d": 5400000000, "flow_20d": 13000000000, "aum": 500000000000},
                {"symbol": "QQQ", "flow_1d": 1600000000, "flow_5d": 5000000000, "flow_20d": 12000000000, "aum": 300000000000},
                {"symbol": "XLP", "flow_1d": -100000000, "flow_5d": -250000000, "flow_20d": -450000000, "aum": 25000000000},
                {"symbol": "HYG", "flow_1d": 200000000, "flow_5d": 600000000, "flow_20d": 1800000000, "aum": 20000000000},
            ],
            {"put_call_ratio": 0.5, "equity_put_call_ratio": 0.55, "index_put_call_ratio": 0.6, "call_volume": 15000000, "put_volume": 6000000},
            [{"asset": "ES", "net_spec_position": 310000, "net_position_percentile": 0.92}, {"asset": "NQ", "net_spec_position": 260000, "net_position_percentile": 0.9}],
            [{"symbol": "TSLA", "short_interest_percent_float": 0.02, "days_to_cover": 0.5}, {"symbol": "NVDA", "short_interest_percent_float": 0.015, "days_to_cover": 0.4}],
            {"gross_exposure": 1.9, "net_exposure": 1.3, "cash_level": 0.02},
        )
    if name == "crowded_short":
        return _payload(
            [
                {"symbol": "SPY", "flow_1d": -1800000000, "flow_5d": -5600000000, "flow_20d": -13000000000, "aum": 500000000000},
                {"symbol": "QQQ", "flow_1d": -1600000000, "flow_5d": -5000000000, "flow_20d": -12000000000, "aum": 300000000000},
                {"symbol": "XLP", "flow_1d": 250000000, "flow_5d": 600000000, "flow_20d": 1000000000, "aum": 25000000000},
                {"symbol": "HYG", "flow_1d": -500000000, "flow_5d": -1600000000, "flow_20d": -3500000000, "aum": 20000000000},
            ],
            {"put_call_ratio": 1.8, "equity_put_call_ratio": 1.9, "index_put_call_ratio": 1.7, "call_volume": 5000000, "put_volume": 18000000},
            [{"asset": "ES", "net_spec_position": -340000, "net_position_percentile": 0.1}, {"asset": "NQ", "net_spec_position": -270000, "net_position_percentile": 0.15}],
            [{"symbol": "TSLA", "short_interest_percent_float": 0.22, "days_to_cover": 6.2}, {"symbol": "NVDA", "short_interest_percent_float": 0.16, "days_to_cover": 5.4}],
            {"gross_exposure": 0.8, "net_exposure": -0.7, "cash_level": 0.3},
        )
    if name == "mixed_positioning":
        return _payload(
            [
                {"symbol": "SPY", "flow_1d": 200000000, "flow_5d": -300000000, "flow_20d": 1000000000, "aum": 500000000000},
                {"symbol": "QQQ", "flow_1d": -100000000, "flow_5d": 200000000, "flow_20d": 700000000, "aum": 300000000000},
                {"symbol": "XLP", "flow_1d": 30000000, "flow_5d": 50000000, "flow_20d": 100000000, "aum": 25000000000},
                {"symbol": "HYG", "flow_1d": 50000000, "flow_5d": -120000000, "flow_20d": 400000000, "aum": 20000000000},
            ],
            {"put_call_ratio": 1.0, "equity_put_call_ratio": 1.05, "index_put_call_ratio": 0.95, "call_volume": 9000000, "put_volume": 9500000},
            [{"asset": "ES", "net_spec_position": 80000, "net_position_percentile": 0.55}, {"asset": "NQ", "net_spec_position": -20000, "net_position_percentile": 0.45}],
            [{"symbol": "TSLA", "short_interest_percent_float": 0.08, "days_to_cover": 2.5}, {"symbol": "NVDA", "short_interest_percent_float": 0.05, "days_to_cover": 1.8}],
            {"gross_exposure": 1.2, "net_exposure": 0.1, "cash_level": 0.12},
        )
    if name == "low_signal":
        return _payload(
            [
                {"symbol": "SPY", "flow_1d": 0, "flow_5d": 0, "flow_20d": 0, "aum": 500000000000},
                {"symbol": "XLP", "flow_1d": 0, "flow_5d": 0, "flow_20d": 0, "aum": 25000000000},
            ],
            {"put_call_ratio": 1.0, "equity_put_call_ratio": 1.0, "index_put_call_ratio": 1.0, "call_volume": 1000000, "put_volume": 1000000},
            [{"asset": "ES", "net_spec_position": 0, "net_position_percentile": 0.5}],
            [{"symbol": "TSLA", "short_interest_percent_float": 0.0, "days_to_cover": 0.0}],
            {"gross_exposure": 1.0, "net_exposure": 0.0, "cash_level": 0.15},
        )
    raise ValueError(f"Unknown scenario: {name}")
