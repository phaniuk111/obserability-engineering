-- Lab 5. Sampling (ch15). otel_traces holds every span; otel_traces_sampled holds what tail
-- sampling kept: all traces with an error, all slower than 500 ms, 10% of the rest.

-- 5a. What was kept.
SELECT (SELECT uniqExact(TraceId) FROM otel.otel_traces WHERE Timestamp > now() - INTERVAL 30 MINUTE) AS true_traces,
       (SELECT uniqExact(TraceId) FROM otel.otel_traces_sampled WHERE Timestamp > now() - INTERVAL 30 MINUTE) AS kept_traces,
       round(kept_traces / true_traces * 100, 1) AS kept_percent;

-- 5b. Naive counts from sampled data are wrong; weighted counts are close. A kept trace
-- that is neither an error nor slow was a 1-in-10 pick, so it stands for 10 traces.
WITH per_trace AS
(
    SELECT TraceId, max(StatusCode IN ('Error', 'STATUS_CODE_ERROR')) AS has_error, max(Duration) > 500e6 AS slow
    FROM otel.otel_traces_sampled WHERE Timestamp > now() - INTERVAL 30 MINUTE GROUP BY TraceId
)
SELECT count() AS naive_total, sum(if(has_error OR slow, 1, 10)) AS weighted_estimate,
       (SELECT uniqExact(TraceId) FROM otel.otel_traces WHERE Timestamp > now() - INTERVAL 30 MINUTE) AS true_total,
       round(countIf(has_error) / naive_total * 100, 1) AS naive_error_percent,
       round(countIf(has_error) / weighted_estimate * 100, 2) AS weighted_error_percent
FROM per_trace;

-- 5c. Every error survived sampling.
SELECT (SELECT uniqExact(TraceId) FROM otel.otel_traces WHERE StatusCode IN ('Error', 'STATUS_CODE_ERROR') AND Timestamp > now() - INTERVAL 30 MINUTE) AS error_traces,
       (SELECT uniqExact(TraceId) FROM otel.otel_traces_sampled WHERE StatusCode IN ('Error', 'STATUS_CODE_ERROR') AND Timestamp > now() - INTERVAL 30 MINUTE) AS error_traces_kept;
