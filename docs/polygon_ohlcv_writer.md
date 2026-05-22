# Polygon OHLCV Writer

`app/writers/ohlcv_writer.py` is the approved writer boundary for manual Polygon OHLCV persistence.

## Scope

The writer:

- accepts normalized OHLCV records
- deduplicates duplicate natural keys within a batch
- writes to the approved `canonical_ohlcv` contract when the approved table exists
- upserts on `symbol_id + timestamp + timeframe + adjusted`
- commits once per batch
- rolls back on failure

## Safety

The writer does not:

- create tables
- run migrations
- call vendor APIs
- run ingestion pipelines
- start schedulers
- expose API routes
- perform AI or trading logic

`ai-market-machine-data` remains the schema owner.
