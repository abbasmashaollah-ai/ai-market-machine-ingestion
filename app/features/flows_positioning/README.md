# flows_positioning

Dry-run flows and positioning evidence slice.

This package converts fixture positioning inputs into deterministic evidence objects and reports.

The slice is modular because flows evidence spans distinct subdomains:
- ETF flows
- options positioning
- futures positioning
- short interest
- fund exposure

The current implementation remains fixture/dry-run only and keeps the boundary clean:
- no vendor calls
- no database writes
- no scheduler activation
- no AI decision logic
- no trading, capital, or portfolio logic

It is evidence-only:
- no AI decision
- no trading signal
- no vendor calls
- no database writes
