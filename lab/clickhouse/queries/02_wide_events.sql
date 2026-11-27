-- Lab 2. One wide event per request, so any attribute is a GROUP BY (ch1, ch5).

-- 2a. Cardinality: how many distinct values does each attribute have? User id is high, and that is fine here.
SELECT k AS attribute, uniqExact(v) AS distinct_values, count() AS events
FROM otel.otel_traces ARRAY JOIN mapKeys(SpanAttributes) AS k, mapValues(SpanAttributes) AS v
WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout' AND Timestamp > now() - INTERVAL 30 MINUTE
GROUP BY k ORDER BY distinct_values DESC;

-- 2b. A question nobody planned for: latency by tier x payment method x platform.
SELECT SpanAttributes['app.user.tier'] AS tier, SpanAttributes['app.payment.method'] AS method,
       SpanAttributes['app.client.platform'] AS platform, count() AS n,
       round(quantile(0.5)(Duration) / 1e6) AS p50_ms, round(quantile(0.99)(Duration) / 1e6) AS p99_ms
FROM otel.otel_traces
WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout' AND Timestamp > now() - INTERVAL 30 MINUTE
GROUP BY tier, method, platform ORDER BY p99_ms DESC LIMIT 10;

-- 2c. Which single users had the worst time? Impossible with a metric label, trivial here.
SELECT SpanAttributes['app.user.id'] AS user, count() AS requests,
       countIf(StatusCode IN ('Error', 'STATUS_CODE_ERROR')) AS errors, round(max(Duration) / 1e6) AS worst_ms
FROM otel.otel_traces
WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout' AND Timestamp > now() - INTERVAL 30 MINUTE
GROUP BY user ORDER BY errors DESC, worst_ms DESC LIMIT 5;

-- 2d. Why you keep raw events: the average of per-group averages is not the average.
SELECT round(avg(group_avg_ms), 1) AS avg_of_averages, round(sum(group_avg_ms * n) / sum(n), 1) AS true_average
FROM (SELECT SpanAttributes['app.discount.format'] AS g, avg(Duration) / 1e6 AS group_avg_ms, count() AS n
      FROM otel.otel_traces
      WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout' AND Timestamp > now() - INTERVAL 30 MINUTE
      GROUP BY g);
