-- Lab 1. Traces are rows. A trace view is "SELECT ... WHERE TraceId = X ORDER BY Timestamp" (ch6).
-- StatusCode / SpanKind spellings differ between exporter versions, so both are accepted.

-- 1a. The slowest checkouts in the last 30 minutes.
SELECT TraceId, round(Duration / 1e6, 1) AS ms, StatusCode,
       SpanAttributes['app.user.id'] AS user, SpanAttributes['app.discount.format'] AS discount
FROM otel.otel_traces
WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout'
  AND SpanKind IN ('Server', 'SPAN_KIND_SERVER') AND Timestamp > now() - INTERVAL 30 MINUTE
ORDER BY Duration DESC
LIMIT 5;

-- 1b. A waterfall for the slowest one: every span, offset from the trace start.
WITH (SELECT TraceId FROM otel.otel_traces
      WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout'
        AND Timestamp > now() - INTERVAL 30 MINUTE
      ORDER BY Duration DESC LIMIT 1) AS tid
SELECT ServiceName, SpanName, SpanKind,
       round(dateDiff('microsecond', min(Timestamp) OVER (), Timestamp) / 1000, 1) AS start_ms,
       round(Duration / 1e6, 1) AS ms, StatusCode, ParentSpanId != '' AS has_parent
FROM otel.otel_traces
WHERE TraceId = tid
ORDER BY Timestamp;

-- 1c. Async work is a separate trace joined by a span link (not a parent).
SELECT r.SpanName AS job, r.TraceId AS job_trace, r.`Links.TraceId`[1] AS caused_by_trace,
       c.SpanAttributes['app.order.id'] AS order_id
FROM otel.otel_traces AS r
INNER JOIN otel.otel_traces AS c ON c.TraceId = r.`Links.TraceId`[1] AND c.SpanId = r.`Links.SpanId`[1]
WHERE r.SpanName = 'send_receipt' AND r.Timestamp > now() - INTERVAL 30 MINUTE
LIMIT 3;

-- 1d. Baggage: the tier set in storefront shows up on the payments span without an API change.
SELECT s.SpanAttributes['app.user.tier'] AS tier_at_storefront, p.SpanAttributes['app.user.tier'] AS tier_at_payments, count() AS n
FROM otel.otel_traces AS s
INNER JOIN otel.otel_traces AS p ON p.TraceId = s.TraceId
WHERE s.ServiceName = 'storefront' AND s.SpanAttributes['http.route'] = '/checkout'
  AND p.ServiceName = 'payments' AND p.SpanAttributes['http.route'] = '/charge'
  AND s.Timestamp > now() - INTERVAL 30 MINUTE
GROUP BY 1, 2 ORDER BY n DESC;
