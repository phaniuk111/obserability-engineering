-- Lab 4. An event-based SLI (ch11, ch12): "a checkout is good if it succeeds within 500 ms".
-- Each event is good, bad, or not eligible. Target for the lab: 99%.

-- 4a. SLI, error budget and burn rate over the last 30 minutes.
SELECT count() AS eligible,
       countIf(NOT (StatusCode IN ('Error', 'STATUS_CODE_ERROR') OR Duration > 500e6)) AS good,
       eligible - good AS bad,
       round(good / eligible * 100, 3) AS sli_percent,
       round(eligible * (1 - 0.99), 1) AS budget_events,
       round(bad / (eligible * (1 - 0.99)) * 100, 1) AS budget_spent_percent,
       round((bad / eligible) / (1 - 0.99), 2) AS burn_rate
FROM otel.otel_traces
WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout'
  AND SpanKind IN ('Server', 'SPAN_KIND_SERVER') AND Timestamp > now() - INTERVAL 30 MINUTE;

-- 4b. The same budget minute by minute, so you can see when the burn started.
SELECT toStartOfMinute(Timestamp) AS minute, count() AS eligible,
       countIf(StatusCode IN ('Error', 'STATUS_CODE_ERROR') OR Duration > 500e6) AS bad,
       round((bad / eligible) / (1 - 0.99), 1) AS burn_rate
FROM otel.otel_traces
WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout'
  AND SpanKind IN ('Server', 'SPAN_KIND_SERVER') AND Timestamp > now() - INTERVAL 30 MINUTE
GROUP BY minute ORDER BY minute;

-- 4c. Time-based vs event-based (ch12): a minute whose P95 is over 500 ms counts as a
-- fully bad minute in a time-based SLO, even if most requests in it were fine.
SELECT count() AS minutes, countIf(p95_ms > 500) AS bad_minutes,
       round(bad_minutes / minutes * 100, 1) AS time_based_bad_percent,
       round(sum(bad) / sum(n) * 100, 1) AS event_based_bad_percent
FROM (SELECT toStartOfMinute(Timestamp) AS minute, count() AS n, quantile(0.95)(Duration) / 1e6 AS p95_ms,
             countIf(StatusCode IN ('Error', 'STATUS_CODE_ERROR') OR Duration > 500e6) AS bad
      FROM otel.otel_traces
      WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout'
        AND SpanKind IN ('Server', 'SPAN_KIND_SERVER') AND Timestamp > now() - INTERVAL 30 MINUTE
      GROUP BY minute);
