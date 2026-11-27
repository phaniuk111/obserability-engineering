-- Lab 7. Why this is cheap (ch13, ch14): parts, sorting key, compression.

-- 7a. Parts and compression for the traces table.
SELECT count() AS active_parts, sum(rows) AS rows,
       formatReadableSize(sum(data_uncompressed_bytes)) AS raw, formatReadableSize(sum(data_compressed_bytes)) AS on_disk,
       round(sum(data_uncompressed_bytes) / sum(data_compressed_bytes), 1) AS compression_ratio
FROM system.parts WHERE database = 'otel' AND table = 'otel_traces' AND active;

-- 7b. The keys that decide what is fast. Small parts are stored in "Compact" form (all
-- columns in one file); they become "Wide" (one file per column) as they grow.
SELECT sorting_key, partition_key, (SELECT groupUniqArray(part_type) FROM system.parts WHERE database = 'otel' AND table = 'otel_traces' AND active) AS part_types
FROM system.tables WHERE database = 'otel' AND name = 'otel_traces';

-- 7c. The sorting key decides what is fast. A filter on the first key column reads few granules...
EXPLAIN indexes = 1
SELECT count() FROM otel.otel_traces WHERE ServiceName = 'payments' AND SpanName = 'validate_discount';

-- 7d. ...a filter only on an attribute has to scan. This is where a skip index or a
-- materialized column earns its place.
EXPLAIN indexes = 1
SELECT count() FROM otel.otel_traces WHERE SpanAttributes['app.user.id'] = 'u-00042';
