# Chapter 13: Storage: Honeycomb's Retriever

Part 4: Technical deep dives. Coverage: Read in full from the book; text paraphrased.

## Summary

Requirements: answers in seconds; every field queryable at full resolution; no privileged dimension except time (and tenant/service); fresh data within seconds; durable and fault-tolerant, even when your own infrastructure is failing.

TSDBs explode on cardinality, since every unique tag combination is a new series. NoSQL needs indexes on everything. Scuba used RAM: about $5k/TB vs under $50/TB for SSD. Bigtable-style row stores need compaction, and Dapper's indexes on just three fields were 76% the size of the data.

Retriever's hybrid: append-only segments per tenant, closed at 1 hour, 250k rows or 1 GB, with min/max timestamps for pruning. Inside each segment, one file per column, scanned row-at-a-time and aggregated per segment, then merged into a top-K.

## Key ideas

- Encodings: dictionary, sparse/presence bitmaps, run-length, delta, roaring bitmaps for booleans, IDs as integers, then LZ4 (decompression speed matters more than ratio).
- Avoid one-off columns like timestamp_2025…. Use a key/value instead.
- Read-time calculated fields: COALESCE($session.id, $session_id) for renames; regex extraction for legacy logs.
- Trace lookup is just WHERE trace_id = X. Joins work only within a trace (same partition), using a sliding memory window.
- Freshness: queries can force-flush open column files. Ingest and query share only the filesystem.
- Closed segments go to S3. Queries fan out over Lambda in a MapReduce style. When 90% have answered, the slow 10% are re-issued and the first copy back wins.
- Kafka gives an ordered, durable buffer. Stateless receivers feed deterministic indexers, which can be replayed from an offset.
- Scale (Nov 2025): about 1.5 PB, over 1B segments, 3–5M spans/s ingested, median query 50 ms, P99 5 s.
- Complex aggregates need sketches: t-digest for percentiles like P99, HyperLogLog for COUNT DISTINCT.
- Other columnar engines used for observability: ClickHouse, Google BigQuery, Apache Druid. Observe Inc. built on Snowflake (great for warehousing, less interactive).

## You will learn

- State the storage requirements for observability
- Explain why TSDBs, NoSQL and row stores fall short
- Describe Retriever's segments, columns, query path, tiering and durability

## Claims and numbers

| Figure | Context |
|---|---|
| 1 h / 250k / 1 GB | Segment finalisation thresholds |
| 76% | Dapper index size vs trace data |
| $5,000 vs <$50 | 1 TB RAM vs SSD |
| 1.5 PB | Retriever data (Nov 2025) |
| 3–5M/s | Spans ingested |
| 50 ms / 5 s | Median / P99 query |

## Terms

| Term | Meaning |
|---|---|
| Segment | Append-only, time-bounded chunk of a tenant's events |
| Lazy/late materialisation | Read output columns only for matching rows |
| Hedged request | Duplicate a slow request; first wins |
| HyperLogLog | Probabilistic sketch for COUNT DISTINCT |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Dremel / ColumnIO / Bigtable | Google columnar / row stores | BigQuery / Bigtable |
| Grafana Tempo | Trace store | Amazon Managed Grafana + Tempo |
| Chord | Consistent-hashing ring for reducers | n/a |
| Roaring bitmaps | Compressed bitsets | n/a |
| RPC impatience | Hedged requests on stragglers | Lambda retries/hedging pattern |
| HyperLogLog | Approximate COUNT DISTINCT | Athena approx_distinct |
| Apache Druid / BigQuery | Other columnar engines | Amazon Redshift / Athena |

## Interview line

> Partition by time into append-only segments, store each field as its own column, prune by time, read only referenced columns, aggregate per segment in parallel, merge, top-K. Tier closed segments to object storage and hedge slow reads.

## AWS mapping

- S3 for segments; Lambda for map; EC2 Graviton for ingest/query; MSK for Kafka
- DIY equivalent: Parquet on S3 partitioned by hour + Athena

## Practice question

**Q.** Design storage for 3M spans/s with arbitrary GROUP BY in seconds.

**Model answer.** Kafka ingest, partitioned by trace ID. Indexers write time-bounded segments with one compressed column file each, dictionary-encoded. Recent segments stay on SSD and can be queried open; closed ones go to S3. Queries prune by time, then fan out over serverless workers, aggregate per segment, merge and top-K, with stragglers hedged. No indexes except time.

## Exercise

Lab 7: run `make q F=07_storage`, add a bloom-filter skip index on the attribute values, and compare the plan for query 7d.

## Takeaways

- Only time is privileged
- Columns + segments + parallel scans
- Wrong abstraction = hard problems

## Hands-on

[Lab 7: Storage](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/07-storage.md)
