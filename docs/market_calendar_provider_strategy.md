# Market Calendar Provider Strategy

The selected direction is a hybrid calendar approach.

## Strategy

- use a trusted exchange-calendar source or library later to generate schedules
- verify and freeze the resulting calendar through `ai-market-machine-data`
- ingestion consumes the verified calendar consistently
- the current minimal helper remains fallback and manual-only until the production calendar exists

## Ownership

`ai-market-machine-data` owns the persisted production calendar schema.

## Shared use

The same verified calendar must drive:

- daily updates
- backfills
- flat-file coverage validation
- scheduler decisions
- gap-fill logic

## Safety

This strategy does not:

- add trading or AI decision logic
- call external services
- write to the database
- add API routes
- enable the scheduler

`ai-market-machine-data` remains the schema owner.
