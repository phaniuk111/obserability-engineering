# Chapter 5: Structured events are the building blocks

Part 2: Instrumentation fundamentals. Coverage: Read in full from the book; text paraphrased.

## Summary

A structured event is a flat set of key-value pairs describing one unit of work. Think of a database row.

Metrics (born with SNMPv1 in 1988) are numbers plus tags, aggregated into time buckets. They're cheap and predictable but lossy. Logs are text built for humans; structure them and they become events. Traces are 'fancy logs plus passing IDs around'.

So capture one wide event and derive the metric, the log narrative or the trace when you need it. 'When you pre-decide the shape, you pre-decide the investigation.'

## Key ideas

- Counters add up (112 + 78 = 190). Gauges keep the last value. Averages don't combine: per-instance averages of 120/230/200 ms naively give 183 ms, but with counts of 100/57/98 the true average is about 175 ms. A histogram (count + sum) has to be set up before you need it.
- Structured log vs structured event: same thing. The only difference is whether your store treats it as structured data or a string.
- Span fields: trace ID, span ID, parent ID (absent at the root), start timestamp, duration. Plus service name, span name and attributes.
- Propagation: explicit ctx in Go, thread-locals in Python/Ruby, AsyncLocalStorage in Node.
- From one span you can compute P99 per minute with PERCENTILE_DISC, add region to GROUP BY with no schema change, use t-digest or HDR histograms for streaming, and stitch traces by trace ID.

## You will learn

- Show metrics, logs and traces are all structured events
- Explain the average-of-averages trap and how histograms fix it
- Name the five fields a span needs and how context propagates

## Claims and numbers

| Figure | Context |
|---|---|
| 183 vs 175 ms | Naive vs correct cross-instance average |
| 1988 | SNMPv1 introduces the metric |
| 5 | Required span fields |

## Terms

| Term | Meaning |
|---|---|
| Structured event | Flat key-value record of one unit of work |
| Span | One timed operation in a trace |
| Trace context | Trace ID + span ID (+ parent) propagated across work |
| Histogram metric | Buckets plus count and sum, combinable across instances |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| SNMPv1 / RFC 1157 (1988) | Origin of the metric | CloudWatch metrics |
| t-digest / HDR histogram | Streaming quantile sketches | CloudWatch percentiles use sketches |
| AsyncLocalStorage | Node.js implicit context | ADOT Node SDK uses it |

## Interview line

> A trace is just structured logs that share a trace ID and point at their parent. If I store wide events, I can derive any metric, including P99 by region, after the fact. Pre-aggregated metrics can't be un-aggregated.

## AWS mapping

- Logs Insights: `stats pct(duration_ms,99) by bin(1m), region` over JSON events
- X-Ray segments = spans

## Practice question

**Q.** Three instances report average latency 120, 230 and 200 ms. Your manager says the service average is 183 ms. Respond.

**Model answer.** That's an average of averages. It's only right if every instance served the same number of requests. With counts of 100, 57 and 98 the weighted mean is 44,710 / 255 ≈ 175 ms. Fix it by emitting histograms (count + sum), or better, raw events, so you can compute it any way later.

## Exercise

Run pocs/02_mini_tracer and pocs/01_wide_events tests; then extend the tracer to record span events.

## Takeaways

- One record, many views
- Aggregation is the defining strength and weakness of metrics
- Traces = logs + IDs + parent links
