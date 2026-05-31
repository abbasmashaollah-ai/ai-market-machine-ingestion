# Future Domain Build Order

Recommended order for future ingestion vertical slices:

1. symbol master
   - verified through Polygon live population
2. ETF/index universe expansion
   - verified with proxy-mapped index labels and ETF coverage checks
3. Polygon flat-file OHLCV
4. FRED macro
   - verified through live population evidence
5. volatility indexes
   - blocked pending source access and entitlement confirmation
6. event calendars/earnings
   - OPEX deterministic slice verified
   - CPI/FOMC/NFP macro-event planning next
   - earnings calendar planning next
   - event calendar paused cleanly pending the approved data-side contract
   - earnings calendar readiness checkpoint before live adapters
7. fundamentals/filings
   - paused at readiness checkpoint
   - persistence deferred until the approved data-side contract exists
8. news/sentiment
   - paused at readiness checkpoint
   - persistence deferred until the approved data-side contract exists
9. cross-asset OHLCV
   - paused at readiness checkpoint
   - persistence deferred until the approved data-side asset-scope contract exists
10. breadth/participation
   - paused at readiness checkpoint
   - persistence deferred until the approved data-side contract exists
11. options
   - paused at readiness checkpoint
   - persistence deferred until the approved data-side contract exists
12. flows/positioning
   - paused at readiness checkpoint
   - planning coverage complete
   - next phase: data-side contracts and live-adapter prioritization

Planning sweep complete.
Next phase: data-side contract prioritization.
Recommended first contract/adapters:
- event calendar if continuing the event domain
- news/sentiment if product-facing feed is priority
- fundamentals/filings if ticker analyzer depth is priority
- cross-asset OHLCV if market regime coverage is priority

This order prioritizes shared contracts and reusable producer foundations before higher-variance domains.
