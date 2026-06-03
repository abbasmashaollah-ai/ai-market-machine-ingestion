# Volatility Index Alternate Source Review

Purpose:
- determine whether the repo already contains a non-Polygon source path that can support `VIX`, `VVIX`, `VXN`, and `RVX`
- stay within discovery/reporting only
- keep writer/persistence blocked until a valid source is confirmed

Observed Polygon result:
- the most recent live dry run returned `403` for `VIX`, `VVIX`, `VXN`, and `RVX`
- the run produced `fetched_count=0`, `accepted_count=0`, `rejected_count=0`
- the run reported `error_categories=['vendor_error']`
- the run preserved safety boundaries: `no_db_writes=true`, `no_scheduler_activation=true`, `no_persistence=true`

Existing adapters found:
- Polygon volatility adapter and mapping code in `app/vendors/polygon_volatility_index.py`
- Polygon volatility ingestion planner in `app/ingestion/volatility/polygon.py`
- generic FRED vendor foundation in `app/vendors/fred/`
- generic FMP vendor client in `app/vendors/fmp/`
- generic vendor transport and error helpers in `app/vendors/common/`

Candidate alternate sources found:
- Cboe is documented as a planned volatility source candidate
- manual fixture exists for test-only planning
- FRED exists as a vendor foundation, but only for macro series in this repo
- FMP exists as a vendor foundation/client, but not as a volatility-index source in this repo

Candidate alternate sources not found:
- no implemented non-Polygon volatility adapter for `VIX`, `VVIX`, `VXN`, or `RVX`
- no documented FRED volatility series path for these symbols
- no documented Cboe volatility adapter path in code
- no Yahoo, Stooq, or Nasdaq volatility adapter path in code
- no alternate source mapping that already provides stable symbol conversion for the four starter symbols

Coverage assessment:
- `VIX`: covered only by Polygon mapping and planned Cboe discussion
- `VVIX`: covered only by Polygon mapping and planned Cboe discussion
- `VXN`: covered only by Polygon mapping and planned Cboe discussion
- `RVX`: covered only by Polygon mapping and planned Cboe discussion
- no alternate source in repo currently demonstrates full four-symbol coverage

Historical and daily close feasibility:
- Polygon path is designed for historical and daily close/value retrieval, but is currently entitlement-blocked
- FRED foundation in this repo is macro-only and does not show a volatility series equivalent
- FMP foundation in this repo is generic, but no volatility-index coverage or close/value mapping is documented
- Cboe would be the most plausible native fit, but no implemented adapter exists in repo

Entitlement and licensing uncertainty:
- Polygon entitlement is currently not sufficient for the live VIX-family path
- Cboe, FRED, and FMP paths in repo are not proven for these symbols
- there is no repo evidence here that the licensing or entitlement terms are already resolved for a non-Polygon source

Lineage and source attribution feasibility:
- the existing Polygon path already carries source and vendor-symbol mapping semantics
- the generic FRED and FMP foundations can support lineage in principle, but not for these volatility symbols without a source-specific adapter
- stable source attribution is not yet feasible for a non-Polygon VIX-family path because the needed adapter does not exist

Recommended source path:
- continue with Polygon entitlement confirmation only if the organization wants to invest in that path
- otherwise the next realistic fallback is a new Cboe-oriented implementation, but that is not present yet
- do not treat FRED or FMP as validated substitutes for the VIX-family observations in this repo

Can implementation proceed now?
- no
- writer remains blocked until a valid source is confirmed

Decision needed if blocked:
- choose between Polygon entitlement remediation and a new source implementation decision
- if a non-Polygon path is preferred, approve a dedicated adapter/source contract first

Non-goals:
- no DB writes
- no scheduler activation
- no `ai-market-machine-data` changes
- no AI Machine changes
- no live vendor calls
