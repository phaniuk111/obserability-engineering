-- Lab 6. The pipeline changed the data on the way in (ch16, ch31).

-- 6a. The Collector hashed user.email: nothing stored should still contain an "@".
SELECT countIf(SpanAttributes['user.email'] != '') AS events_with_email,
       countIf(position(SpanAttributes['user.email'], '@') > 0) AS still_plaintext,
       any(SpanAttributes['user.email']) AS example_stored_value
FROM otel.otel_traces
WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout' AND Timestamp > now() - INTERVAL 30 MINUTE;

-- 6b. Hashing is consistent, so you can still count distinct customers and join on the value.
SELECT uniqExact(SpanAttributes['app.user.id']) AS distinct_users, uniqExact(SpanAttributes['user.email']) AS distinct_hashed_emails
FROM otel.otel_traces
WHERE ServiceName = 'storefront' AND SpanAttributes['http.route'] = '/checkout' AND Timestamp > now() - INTERVAL 30 MINUTE;
