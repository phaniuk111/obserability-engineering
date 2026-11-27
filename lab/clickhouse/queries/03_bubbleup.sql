-- Lab 3. The core analysis loop, automated (ch8): take the "bad" requests, compare every
-- attribute value's share inside that set with its share in the rest, sort by the gap.
-- No hypothesis needed, and no knowledge of the system.
WITH base AS
(
    SELECT SpanAttributes, (StatusCode IN ('Error', 'STATUS_CODE_ERROR') OR Duration > 500e6) AS bad
    FROM otel.otel_traces
    WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout'
      AND SpanKind IN ('Server', 'SPAN_KIND_SERVER') AND Timestamp > now() - INTERVAL 30 MINUTE
),
totals AS (SELECT countIf(bad) AS bad_total, countIf(NOT bad) AS good_total FROM base)
SELECT k AS attribute, v AS value,
       countIf(bad) AS in_bad, countIf(NOT bad) AS in_good,
       round(in_bad / any(bad_total), 3) AS share_of_bad,
       round(in_good / any(good_total), 3) AS share_of_good,
       round(share_of_bad - share_of_good, 3) AS gap
FROM base ARRAY JOIN mapKeys(SpanAttributes) AS k, mapValues(SpanAttributes) AS v
CROSS JOIN totals
WHERE k LIKE 'app.%'
GROUP BY k, v
ORDER BY gap DESC
LIMIT 8;
