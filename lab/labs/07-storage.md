# Lab 7: storage (ch13, ch14)

**Goal:** connect the queries you have been running to why they are cheap.

`make q F=07_storage`

- **7a** parts, rows and compression. On a tiny dataset I saw about 9x; the book quotes 10–20x and more at scale. Each insert makes an immutable sorted part; background merges combine them.
- **7b** the sorting key, `(ServiceName, SpanName, toDateTime(Timestamp))`, and the partition key (by day).
- **7c** a filter on the leading key columns. The plan's `Indexes` section shows the primary key being used to skip granules (blocks of 8,192 rows by default).
- **7d** a filter only on an attribute inside the map. No key helps: it scans. This is the case for a skip index (bloom filter on the map values) or for promoting a hot attribute to its own column.

Why columnar wins here: a query such as lab 2b touches four columns out of twenty-two, and similar values sit together, so they compress well. ClickHouse docs: [MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree).

**Check yourself**

- You mostly look up by trace id. What would you change? (A bloom-filter skip index on `TraceId`, or a projection / second table ordered by it.)
- What does TTL do here, and how do you keep it cheap? (Drops data after 3 days in the lab; `ttl_only_drop_parts` so whole parts are removed instead of rewritten.)
- How does Honeycomb's Retriever differ? (Segments per time window, one file per column, object storage for closed segments, fan-out to many workers: same principles, different engine.)

**Try:** `make sql`, then `ALTER TABLE otel_traces ADD INDEX idx_user mapValues(SpanAttributes) TYPE bloom_filter(0.01) GRANULARITY 1; ALTER TABLE otel_traces MATERIALIZE INDEX idx_user;` and rerun 7d.
