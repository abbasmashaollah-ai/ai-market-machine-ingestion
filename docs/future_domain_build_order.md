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
   - current planned domain
11. options
12. flows/positioning

This order prioritizes shared contracts and reusable producer foundations before higher-variance domains.
