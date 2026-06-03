from app.features.volatility.volatility_engine import (
    calculate_composite_volatility_stress_score,
    calculate_equity_volatility_pressure_score,
    calculate_latest_level,
    calculate_nasdaq_volatility_pressure_score,
    calculate_series_change,
    calculate_small_cap_volatility_pressure_score,
    calculate_volatility_of_volatility_score,
    determine_volatility_regime_label,
)


def test_engine_calculations_and_labels() -> None:
    history = [10, 11, 12, 13, 14, 15]
    assert calculate_latest_level(history) == 15.0
    assert calculate_series_change(history, 1) == 1.0
    assert calculate_series_change(history, 5) == 5.0
    assert calculate_volatility_of_volatility_score(vvix_level=80, vvix_change_5d=2) == 2.8
    assert calculate_equity_volatility_pressure_score(vix_level=14, vix_change_5d=-1) == -0.86
    assert calculate_nasdaq_volatility_pressure_score(vxn_level=18, vxn_change_5d=1) == 1.18
    assert calculate_small_cap_volatility_pressure_score(rvx_level=20, rvx_change_5d=0.5) == 0.7
    composite = calculate_composite_volatility_stress_score(
        {
            "volatility_of_volatility_score": 1.0,
            "equity_volatility_pressure_score": 0.5,
            "nasdaq_volatility_pressure_score": 0.25,
            "small_cap_volatility_pressure_score": 0.75,
        }
    )
    assert composite == 0.625
    assert determine_volatility_regime_label(vix_level=12, composite_score=0.1) == "LOW_VOLATILITY"
