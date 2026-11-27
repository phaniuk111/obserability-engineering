# Chapter 14: Storage: ClickHouse

Part 4: Technical deep dives. Coverage: Read in full from the book; text paraphrased.

## Summary

ClickHouse is an open-source columnar DBMS, a single binary where every node can read and write. MergeTree writes one immutable sorted part per insert and merges parts in the background. A sparse primary index stores the first key of each ~8,192-row granule.

A query prunes partitions, then parts (by min/max key), binary-searches the sparse index to find granules, reads only the filter columns, then fetches output columns for matching rows (lazy materialisation). Observability data often compresses 10–20x or more.

Choose the primary key to match how you query: (ServiceName, Timestamp) if you filter by service first. Put hot attributes in real columns, everything else in a Map or the newer JSON type.

## Key ideas

- Caches: query result cache (by AST), query condition cache (a bit per granule per predicate), filesystem cache, userspace page cache.
- Ingest via the OTel Collector exporter. Prefer fewer, bigger inserts (a batch processor at a gateway) or async_insert=1. Inserts are idempotent by block hash, so retries are safe.
- ASOF JOIN connects events at query time with no trace IDs, e.g. container crash to the next ContainerReady gives recovery seconds (nginx 961 s, apiserver 63 s), and per image tag that's MTTR by version.
- Skip indexes: bloom_filter on RequestId (0.1% false positives), bloom on map keys/values, tokenbf_v1 for message tokens, MinMax for outliers. Only worth it when few granules match.
- Projections: hidden copies re-sorted by a different key, chosen automatically. Incremental materialized views: insert triggers that route error logs to a table and aggregate them for alerting. Merge tables give one view over evolving schemas.
- TTL: move to S3 at 90 days, delete at 365. Use ttl_only_drop_parts or weekly partitions so it stays cheap.
- Scale vertically first. Replication via Keeper (Raft) is active-active and eventually consistent (insert_quorum when you need it). Sharding via Distributed tables. Multi-region: shard by region. SharedMergeTree separates storage from compute.
- Sizing: 32 cores/128 GB ≈ 20B events/day, peaking at 300–400k/s. 20 TB raw/day becomes 1–2 TB on disk.
- Example 14-4 result: /api/v1/orders served 40,723 requests with P95 1.034 s and P99 1.78 s, the obvious first target. Grouping by path × version × IP would be impossible as metrics.
- Two servers with 7.5 TB NVMe each (full copies for HA) hold about three days of data before object storage. Load-balancing writes across replicas reaches about 500k events/s.
- Replication uses the ReplicatedMergeTree engine; Map columns typically use CODEC(ZSTD(1)).

## You will learn

- Explain MergeTree, granules and the sparse primary index
- Tune schema: primary key, Map vs JSON, skip indexes, projections, materialized views
- Scale with replication, sharding and SharedMergeTree

## Claims and numbers

| Figure | Context |
|---|---|
| 8,192 | Rows per granule (default) |
| 150 GB | Default max merged part size |
| 20:1 | Typical compression |
| 20B/day | Single 32-core node ingest |
| 300–400k/s | Peak events/s per node |
| 1.034 s / 1.78 s | P95/P99 of the slowest endpoint in Example 14-4 |
| 7.5 TB × 2 | NVMe pair ≈ 3 days before object storage |
| 500k/s | Events/s with write load-balancing |

## Terms

| Term | Meaning |
|---|---|
| Granule | Smallest indexed block of rows |
| Projection | Hidden alternate-order copy chosen by the optimizer |
| ASOF JOIN | Join to nearest preceding/following row |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| MergeTree / granule | Core engine / 8,192-row index unit | ClickHouse Cloud on AWS |
| Keeper | Raft coordination (ZooKeeper replacement) | n/a |
| HyperDX | Open-source ClickHouse observability UI | n/a |
| Dash0 / SigNoz / SolarWinds | Vendors built on ClickHouse | Marketplace |
| LSM tree | Log-structured merge tree | DynamoDB/RocksDB lineage |
| ReplicatedMergeTree | Replicated table engine via Keeper | n/a |

## Interview line

> ClickHouse is good here because parts are immutable and sorted with a sparse index, so time+service queries skip almost everything, and columns not referenced are never read. I evolve the schema with materialised columns, projections and materialised views as query patterns emerge.

## AWS mapping

- ClickHouse Cloud on AWS or self-managed on EC2 with NVMe (i4i/i7ie) + S3 tier
- Alternative: Athena/Iceberg for cold, OpenSearch for search-heavy logs

## Practice question

**Q.** Queries filtering on LogAttributes['pod_name'] are slow. What do you do?

**Model answer.** Map lookups read every key and value. If pod_name is hot, materialise it as a real column (or let the JSON type do it) and add a bloom or set skip index if values cluster by primary key. If it's a primary access path, add a projection ordered by it. Then check with system tables that granules are actually being skipped.

## Exercise

Write the CREATE TABLE for your spans with a primary key matched to your top three queries, and one materialized view for errors.

## Takeaways

- Sort by how you query
- Lazy materialisation for wide events
- Evolve schema with data, not guesses

## Hands-on

[Lab 7: Storage](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/07-storage.md)

## Official documentation

- [ClickHouse MergeTree engine](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree): Parts, granules, sparse primary index
- [MergeTree settings: max_bytes_*](https://clickhouse.com/docs/reference/settings/merge-tree-settings/max-bytes): Where the 150 GB merged-part default comes from
- [Collector ClickHouse exporter](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/clickhouseexporter): The otel_traces schema used in the lab
