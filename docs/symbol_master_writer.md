# Symbol Master Writer

`app.writers.symbol_master_writer.SymbolMasterWriter` is the approved manual persistence boundary for symbol master confirmed writes in `ai-market-machine-ingestion`.

## Responsibilities

- accept `list[app.normalization.symbol_master.NormalizedSymbolMasterRecord]`
- deduplicate by canonical `symbol`
- upsert into `public.symbol_master` by canonical symbol
- commit once per batch
- roll back on failure
- refuse to create tables or run migrations

## Non-responsibilities

- vendor fetching
- normalization
- scheduler ownership
- API routes
- schema ownership
- AI/trading/risk/signal/regime/portfolio logic

## Boundary

The writer only persists already-normalized symbol master records. It does not produce source records and does not infer schema ownership.
