"""Pure certified OHLCV row-to-history transformer for sector rotation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass, replace
from datetime import date, datetime
from collections.abc import Mapping, Sequence

from app.clients.data_read_client import DataReadClient, DataReadClientError
from app.features.sector_rotation.sector_rotation_job import run_sector_rotation_dry_run, SectorRotationDryRunResult
from app.features.sector_rotation.sector_universe import get_required_symbols


_ACCEPTABLE_QUALITY_STATUSES = {"VALID", "WARNING", "PENDING", None}
_ACCEPTABLE_CERTIFICATION_STATUSES = {"CERTIFIED", "PENDING", "UNCERTIFIED", None}
_ACCEPTABLE_FRESHNESS_STATUSES = {"FRESH", "DELAYED", "PENDING", "UNKNOWN", None, "STALE"}


@dataclass(frozen=True, slots=True)
class CertifiedOHLCVRow:
    symbol: str
    date: str | date | datetime
    close: float | int | None
    quality_status: str | None = None
    certification_status: str | None = None
    freshness_status: str | None = None
    source: str | None = None
    lineage: Mapping[str, object] | None = None


@dataclass(frozen=True, slots=True)
class SectorRotationReaderResult:
    price_history_by_symbol: dict[str, list[float | int]]
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SectorRotationCertifiedOHLCVAdapterResult:
    price_history_by_symbol: dict[str, list[float | int]]
    warnings: tuple[str, ...] = field(default_factory=tuple)
    missing_symbols: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True
    dry_run_result: SectorRotationDryRunResult | None = None
    shadow_diagnostic: "SectorRotationShadowDiagnostic | None" = None


@dataclass(frozen=True, slots=True)
class SectorRotationShadowDiagnostic:
    enabled: bool
    universe: str
    evidence_available: bool
    skipped: bool
    route_failure: bool = False
    unauthorized: bool = False
    dataset_version: str | None = None
    schema_version: str | None = None
    certification_status: str | None = None
    validation_status: str | None = None
    coverage_status: str | None = None
    quality_status: str | None = None
    observation_date: str | None = None
    generated_at: str | None = None
    section_availability: dict[str, bool] = field(default_factory=dict)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    differences: tuple[str, ...] = field(default_factory=tuple)


def _build_shadow_diagnostic_disabled(universe: str) -> SectorRotationShadowDiagnostic:
    return SectorRotationShadowDiagnostic(
        enabled=False,
        universe=universe,
        evidence_available=False,
        skipped=True,
    )


def _normalize_section_availability(section: object) -> bool:
    if isinstance(section, Mapping):
        return True
    return False


def _extract_market_feature_bundle_section(bundle: Mapping[str, object], section_name: str) -> bool:
    if section_name in bundle and _normalize_section_availability(bundle.get(section_name)):
        return True
    return False


def _build_shadow_diagnostic_from_bundle(
    *,
    universe: str,
    bundle: Mapping[str, object] | None,
    local_warnings: Sequence[str] | None = None,
    skipped: bool = False,
    route_failure: bool = False,
    unauthorized: bool = False,
) -> SectorRotationShadowDiagnostic:
    if not isinstance(bundle, Mapping):
        return SectorRotationShadowDiagnostic(
            enabled=True,
            universe=universe,
            evidence_available=False,
            skipped=True if skipped else False,
            route_failure=route_failure,
            unauthorized=unauthorized,
            warnings=tuple(local_warnings or ()),
        )

    missing_data_evidence = bundle.get("missing_data_evidence")
    stale_data_evidence = bundle.get("stale_data_evidence")
    if missing_data_evidence not in (None, [], {}) or stale_data_evidence not in (None, [], {}):
        return SectorRotationShadowDiagnostic(
            enabled=True,
            universe=universe,
            evidence_available=False,
            skipped=True,
            warnings=tuple(local_warnings or ()),
        )

    section_availability = {
        section_name: _extract_market_feature_bundle_section(bundle, section_name)
        for section_name in ("prices", "sector_rotation", "market_risk", "market_regime", "macro_liquidity", "flows_positioning")
    }
    compact_summary = bundle.get("compact_summary")
    observation_date = None
    generated_at = None
    if isinstance(bundle.get("observation_date"), str):
        observation_date = str(bundle.get("observation_date"))
    if isinstance(bundle.get("generated_at"), str):
        generated_at = str(bundle.get("generated_at"))

    return SectorRotationShadowDiagnostic(
        enabled=True,
        universe=str(bundle.get("universe") or universe).upper(),
        evidence_available=True,
        skipped=False,
        dataset_version=str(bundle.get("dataset_version")) if bundle.get("dataset_version") is not None else None,
        schema_version=str(bundle.get("schema_version")) if bundle.get("schema_version") is not None else None,
        certification_status=str(bundle.get("certification_status")) if bundle.get("certification_status") is not None else None,
        validation_status=str(bundle.get("validation_status")) if bundle.get("validation_status") is not None else None,
        coverage_status=str(bundle.get("coverage_status")) if bundle.get("coverage_status") is not None else None,
        quality_status=str(bundle.get("quality_status")) if bundle.get("quality_status") is not None else None,
        observation_date=observation_date,
        generated_at=generated_at,
        section_availability=section_availability,
        warnings=tuple(str(warning) for warning in (bundle.get("warnings") or []) if isinstance(warning, str)),
        differences=tuple(),
    )


def _normalize_symbol(symbol: object) -> str:
    if not isinstance(symbol, str):
        return ""
    normalized = symbol.strip().upper()
    if not normalized:
        return ""
    return normalized


def _normalize_timestamp(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _coerce_status(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip().upper()
        return normalized or None
    return str(value).strip().upper() or None


def coerce_certified_ohlcv_row(row: object) -> dict[str, object]:
    """Coerce mapping or dataclass input into a normalized OHLCV row dict."""

    if is_dataclass(row):
        raw = asdict(row)
    elif isinstance(row, Mapping):
        raw = dict(row)
    else:
        raise TypeError("certified OHLCV row must be a mapping or dataclass instance")

    normalized_symbol = _normalize_symbol(raw.get("symbol"))
    normalized_date = raw.get("date", raw.get("timestamp"))
    normalized_close = raw.get("close")
    quality_status = _coerce_status(raw.get("quality_status"))
    certification_status = _coerce_status(raw.get("certification_status"))
    freshness_status = _coerce_status(raw.get("freshness_status"))

    return {
        "symbol": normalized_symbol,
        "date": _normalize_timestamp(normalized_date) if normalized_date is not None else None,
        "close": normalized_close,
        "quality_status": quality_status,
        "certification_status": certification_status,
        "freshness_status": freshness_status,
        "source": raw.get("source"),
        "lineage": dict(raw.get("lineage") or {}),
    }


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _sorted_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    indexed_rows: list[tuple[str, int, dict[str, object]]] = []
    for index, row in enumerate(rows):
        coerced = coerce_certified_ohlcv_row(row)
        indexed_rows.append((str(coerced.get("date") or ""), index, coerced))
    indexed_rows.sort(key=lambda item: (item[0], item[1]))
    return [row for _, _, row in indexed_rows]


def build_price_history_by_symbol(
    rows: Sequence[Mapping[str, object]] | Sequence[object],
    required_symbols: Sequence[str] | None = None,
    min_history_length: int | None = None,
    close_field: str = "close",
) -> SectorRotationReaderResult:
    """Build a price-history map from certified OHLCV rows."""

    required_symbols = tuple(_normalize_symbol(symbol) for symbol in (required_symbols or get_required_symbols()))
    required_symbol_set = {symbol for symbol in required_symbols if symbol}
    warnings: list[str] = []
    accepted_rows: list[dict[str, object]] = []

    for row in rows:
        coerced = coerce_certified_ohlcv_row(row)
        symbol = coerced["symbol"]
        if not symbol or symbol not in required_symbol_set:
            continue

        quality_status = coerced.get("quality_status")
        certification_status = coerced.get("certification_status")
        freshness_status = coerced.get("freshness_status")

        if quality_status not in _ACCEPTABLE_QUALITY_STATUSES:
            warnings.append(f"rejected_quality_status:{symbol}:{quality_status}")
            continue
        if certification_status not in _ACCEPTABLE_CERTIFICATION_STATUSES:
            warnings.append(f"rejected_certification_status:{symbol}:{certification_status}")
            continue
        if freshness_status not in _ACCEPTABLE_FRESHNESS_STATUSES:
            warnings.append(f"rejected_freshness_status:{symbol}:{freshness_status}")
            continue

        close_value = coerced.get(close_field)
        if close_value is None or not _is_number(close_value):
            warnings.append(f"missing_or_invalid_close:{symbol}")
            continue

        accepted_rows.append(coerced)

    accepted_rows = _sorted_rows(accepted_rows)
    price_history_by_symbol: dict[str, list[float | int]] = {symbol: [] for symbol in required_symbols if symbol}
    for row in accepted_rows:
        symbol = str(row["symbol"])
        price_history_by_symbol.setdefault(symbol, []).append(row[close_field])

    populated_symbols = tuple(symbol for symbol, history in price_history_by_symbol.items() if history)
    missing_symbols = get_missing_required_symbols(
        {symbol: price_history_by_symbol[symbol] for symbol in populated_symbols},
        required_symbols=required_symbols,
    )
    if missing_symbols:
        warnings.append(f"missing_required_symbols:{','.join(missing_symbols)}")

    if min_history_length is not None:
        for symbol, history in price_history_by_symbol.items():
            if len(history) < min_history_length:
                warnings.append(f"insufficient_history:{symbol}:{len(history)}<{min_history_length}")

    return SectorRotationReaderResult(price_history_by_symbol=price_history_by_symbol, warnings=tuple(warnings))


def get_missing_required_symbols(
    price_history_by_symbol: Mapping[str, Sequence[object]],
    required_symbols: Sequence[str] | None = None,
) -> tuple[str, ...]:
    required_symbols = tuple(_normalize_symbol(symbol) for symbol in (required_symbols or get_required_symbols()))
    existing_symbols = {_normalize_symbol(existing) for existing in price_history_by_symbol}
    missing = [symbol for symbol in required_symbols if symbol and symbol not in existing_symbols]
    return tuple(missing)


def validate_reader_history_coverage(
    price_history_by_symbol: Mapping[str, Sequence[object]],
    required_symbols: Sequence[str] | None = None,
    min_history_length: int = 61,
) -> tuple[bool, tuple[str, ...]]:
    """Validate symbol coverage and minimum history length for the reader output."""

    warnings: list[str] = []
    missing_symbols = get_missing_required_symbols(price_history_by_symbol, required_symbols=required_symbols)
    if missing_symbols:
        warnings.append(f"missing_required_symbols:{','.join(missing_symbols)}")
    for symbol, history in price_history_by_symbol.items():
        if len(history) < min_history_length:
            warnings.append(f"insufficient_history:{_normalize_symbol(symbol)}:{len(history)}<{min_history_length}")
    return (not warnings, tuple(warnings))


def _extract_rows_from_payload(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("historical_ohlcv", "rows", "data", "ohlcv", "historical", "results"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [row for row in rows if isinstance(row, dict)]
    raise ValueError("data read response did not contain a supported row collection")


def fetch_sector_rotation_price_history(
    data_read_client: DataReadClient,
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = 90,
    required_symbols: Sequence[str] | None = None,
    enable_market_feature_bundle_shadow: bool = False,
    market_feature_bundle_client: DataReadClient | None = None,
) -> SectorRotationCertifiedOHLCVAdapterResult:
    """Fetch certified OHLCV rows one symbol at a time and shape them into the dry-run input."""

    required_symbols = tuple(required_symbols or get_required_symbols(include_benchmark=True))
    warnings: list[str] = []

    combined_rows: list[dict[str, object]] = []
    top_level_warnings: list[str] = []

    try:
        if hasattr(data_read_client, "get_symbol_ohlcv_history"):
            for symbol in required_symbols:
                response = data_read_client.get_symbol_ohlcv_history(
                    symbol,
                    start_date=start_date,
                    end_date=end_date,
                    limit=lookback_days,
                    order="asc",
                )
                rows = _extract_rows_from_payload(response)
                combined_rows.extend(rows)
                if isinstance(response, dict):
                    coverage = response.get("ohlcv_coverage")
                    if isinstance(coverage, dict):
                        coverage_warnings = coverage.get("warnings")
                        if isinstance(coverage_warnings, list):
                            top_level_warnings.extend(str(warning) for warning in coverage_warnings)
                    response_warnings = response.get("warnings")
                    if isinstance(response_warnings, list):
                        top_level_warnings.extend(str(warning) for warning in response_warnings)
        else:
            response = data_read_client.get_certified_ohlcv_history(
                list(required_symbols),
                start_date=start_date,
                end_date=end_date,
                lookback_days=lookback_days,
            )
            combined_rows.extend(_extract_rows_from_payload(response))
    except DataReadClientError as exc:
        raise RuntimeError(f"sector rotation data read failed: {exc}") from exc

    rows = combined_rows
    reader_result = build_price_history_by_symbol(
        rows,
        required_symbols=required_symbols,
        min_history_length=lookback_days if lookback_days is not None else None,
    )
    warnings.extend(top_level_warnings)
    warnings.extend(reader_result.warnings)
    missing_symbols = get_missing_required_symbols(reader_result.price_history_by_symbol, required_symbols=required_symbols)
    if missing_symbols:
        warnings.append(f"adapter_missing_symbols:{','.join(missing_symbols)}")

    shadow_diagnostic = None
    if enable_market_feature_bundle_shadow:
        shadow_source = market_feature_bundle_client or data_read_client
        shadow_diagnostic = build_sector_rotation_shadow_diagnostic(
            shadow_source,
            universe="SPY",
            local_price_history_by_symbol=reader_result.price_history_by_symbol,
            local_warnings=warnings,
        )

    return SectorRotationCertifiedOHLCVAdapterResult(
        price_history_by_symbol=reader_result.price_history_by_symbol,
        warnings=tuple(warnings),
        missing_symbols=missing_symbols,
        shadow_diagnostic=shadow_diagnostic,
    )


def run_sector_rotation_certified_ohlcv_dry_run(
    data_read_client: DataReadClient,
    observation_date: date | datetime | str,
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = 90,
    timestamp: datetime | str | None = None,
    writer: object | None = None,
    metadata: Mapping[str, object] | SectorRotationBuildMetadata | None = None,
    enable_market_feature_bundle_shadow: bool = False,
    market_feature_bundle_client: DataReadClient | None = None,
) -> SectorRotationCertifiedOHLCVAdapterResult:
    """Fetch certified OHLCV rows, shape them, and execute the dry-run pipeline in memory."""

    adapter_result = fetch_sector_rotation_price_history(
        data_read_client,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
        enable_market_feature_bundle_shadow=enable_market_feature_bundle_shadow,
        market_feature_bundle_client=market_feature_bundle_client,
    )
    dry_run_result = run_sector_rotation_dry_run(
        adapter_result.price_history_by_symbol,
        observation_date=observation_date,
        timestamp=timestamp,
        writer=writer,
        metadata=metadata,
    )
    combined_warnings = tuple(adapter_result.warnings) + tuple(dry_run_result.warnings)
    return SectorRotationCertifiedOHLCVAdapterResult(
        price_history_by_symbol=adapter_result.price_history_by_symbol,
        warnings=combined_warnings,
        missing_symbols=adapter_result.missing_symbols,
        dry_run_result=dry_run_result,
        shadow_diagnostic=adapter_result.shadow_diagnostic,
    )


def build_sector_rotation_shadow_diagnostic(
    market_feature_bundle_client: DataReadClient,
    *,
    universe: str = "SPY",
    local_price_history_by_symbol: Mapping[str, Sequence[object]] | None = None,
    local_warnings: Sequence[str] | None = None,
) -> SectorRotationShadowDiagnostic:
    try:
        payload = market_feature_bundle_client.get_market_feature_bundle(universe)
    except Exception as exc:
        return SectorRotationShadowDiagnostic(
            enabled=True,
            universe=_normalize_symbol(universe),
            evidence_available=False,
            skipped=True,
            route_failure=True,
            warnings=tuple(local_warnings or ()) + (f"shadow_error:{_normalize_symbol(universe)}:{exc.__class__.__name__}",),
        )

    if not getattr(payload, "evidence_available", False):
        return _build_shadow_diagnostic_from_bundle(
            universe=_normalize_symbol(getattr(payload, "universe", universe)),
            bundle=None,
            local_warnings=tuple(local_warnings or ()),
            skipped=True,
            route_failure=bool(getattr(payload, "route_failure", False)),
            unauthorized=bool(getattr(payload, "unauthorized", False)),
        )

    bundle = {
        "universe": getattr(payload, "universe", universe),
        "dataset_version": getattr(payload, "dataset_version", None),
        "schema_version": getattr(payload, "schema_version", None),
        "certification_status": getattr(payload, "certification_status", None),
        "validation_status": getattr(payload, "validation_status", None),
        "coverage_status": getattr(payload, "coverage_status", None),
        "quality_status": getattr(payload, "quality_status", None),
        "observation_date": getattr(payload, "observation_date", None),
        "generated_at": getattr(payload, "generated_at", None),
        "compact_summary": getattr(payload, "compact_summary", None),
        "warnings": list(getattr(payload, "warnings", ()) or ()),
        "missing_data_evidence": [],
        "stale_data_evidence": [],
    }
    diagnostic = _build_shadow_diagnostic_from_bundle(
        universe=_normalize_symbol(getattr(payload, "universe", universe)),
        bundle=bundle,
        local_warnings=local_warnings,
    )

    if local_price_history_by_symbol is None:
        return diagnostic

    local_symbol_count = len({symbol for symbol, values in local_price_history_by_symbol.items() if values})
    differences = list(diagnostic.differences)
    if local_symbol_count == 0:
        differences.append("missing_local_price_history")
    api_summary = bundle.get("compact_summary")
    if isinstance(api_summary, Mapping):
        api_sections = api_summary.get("feature_sections_present")
        if isinstance(api_sections, Mapping):
            for key in ("prices", "sector_rotation", "market_risk", "market_regime", "macro_liquidity", "flows_positioning"):
                if not bool(api_sections.get(key)):
                    differences.append(f"missing_api_section:{key}")
    return replace(diagnostic, differences=tuple(differences))
