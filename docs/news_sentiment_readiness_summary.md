# News/Sentiment Readiness Summary

The news/sentiment vertical slice is currently at readiness checkpoint, not at persistence.

## Ready Items

- vertical-slice plan exists
- source plan exists
- fixture-backed dry-run foundation exists
- preflight exists
- evidence plan exists
- manual inventory includes news/sentiment commands

## Normalized Fields

- `news_id`
- `published_at`
- `source`
- `publisher`
- `title`
- `summary`
- `url`
- `tickers`
- `sentiment_label`
- `sentiment_score`
- `raw_source_id`
- `notes`

## Dependencies and Candidates

- symbol_master is the upstream dependency for ticker mapping
- source candidates include Finnhub, FMP, Polygon, and manual_fixture

## Current Boundary

- live vendor adapters are not built yet
- data-side contracts are not yet approved
- persistence is deferred
- no DB reads or DB writes are enabled

## Next Options

- data-side news/sentiment contract
- Finnhub live dry-run planning
- FMP news live dry-run planning

## Boundary Statement

This repository remains on the producer-planning side only.
No AI/trading/risk/signal/regime/portfolio logic belongs in this readiness checkpoint.
