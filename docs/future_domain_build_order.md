# Future Domain Build Order

Recommended order for future ingestion vertical slices:

1. symbol master
   - verified through Polygon live population
2. ETF/index universe expansion
   - verified with proxy-mapped index labels and ETF coverage checks
3. Polygon flat-file OHLCV
4. FRED macro
   - planned next domain after ETF/index universe verification and Polygon flat-file OHLCV foundation
5. volatility indexes
6. event calendars/earnings
7. fundamentals
8. news
9. cross-asset OHLCV
10. breadth/participation
11. options
12. flows/positioning

This order prioritizes shared contracts and reusable producer foundations before higher-variance domains.
