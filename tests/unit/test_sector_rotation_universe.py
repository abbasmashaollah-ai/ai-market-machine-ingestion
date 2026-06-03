import pytest

from app.features.sector_rotation.sector_universe import (
    SPY_BENCHMARK,
    SECTOR_ROTATION_UNIVERSE,
    get_required_symbols,
    get_sector_definition,
    get_sector_symbols,
    get_spdr_sector_definitions,
    is_sector_symbol,
)


def test_sector_rotation_universe_has_exact_eleven_sector_symbols() -> None:
    assert SECTOR_ROTATION_UNIVERSE == "SPDR_SECTORS"
    assert get_sector_symbols() == ("XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLRE", "XLK", "XLU")
    assert len(get_spdr_sector_definitions()) == 11


def test_sector_rotation_required_symbols_include_benchmark_when_requested() -> None:
    assert get_required_symbols() == (SPY_BENCHMARK, "XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLRE", "XLK", "XLU")
    assert get_required_symbols(include_benchmark=False) == ("XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLRE", "XLK", "XLU")


def test_sector_rotation_definition_flags_are_present() -> None:
    xlp = get_sector_definition("xlp")
    assert xlp.is_defensive_sector is True
    assert xlp.is_cyclical_sector is False
    assert xlp.is_growth_sector is False
    assert xlp.is_rate_sensitive_sector is False

    xlk = get_sector_definition("XLK")
    assert xlk.is_growth_sector is True
    assert xlk.is_defensive_sector is False

    xlu = get_sector_definition("xlu")
    assert xlu.is_rate_sensitive_sector is True


def test_sector_rotation_lookup_normalizes_lowercase_input() -> None:
    definition = get_sector_definition("xlk")
    assert definition.symbol == "XLK"
    assert is_sector_symbol("xlk") is True


def test_sector_rotation_unknown_symbol_raises_key_error() -> None:
    with pytest.raises(KeyError):
        get_sector_definition("XYZ")

