# Chapter 15: Cheap and accurate enough sampling

Part 4: Technical deep dives. Coverage: Read in full from the book; text paraphrased.

## Summary

Most events are identical successes. Keep representative good events and every interesting bad one, record the sample rate on each kept event, and rebuild true counts by weighting.

Constant probability (1 in N) is easy, and P50/P99 survive unchanged. It fails when errors matter more than successes, when some customers are 100x louder than others, or when a surge could flood the backend.

Trace decisions must be consistent. Derive the decision from the trace ID so every service keeps or drops the same trace. Head sampling decides with what's known at the start; tail sampling buffers the whole trace (needs a collector); buffered approaches combine both.

## Key ideas

- Dynamic rates break simple multiplication, so use weights: median of values {1,3,7} with rates {5,2,9} is 7, not 3.
- Per-key rates (status, method, customer). Per-key + recent volume (e.g. [customer, dataset, error] counts in the last 30 s). Target-rate (N events/s). Per-key target rates (dynsampler-go).
- Errors and slow requests (>500 ms) get their own budget. Ordinary ones are rate-limited.
- Parents pass the head decision and rate to children. A Redis child sampled at 1/1000 never orphans when its parent is 1/10.
- Strategy depends on traffic shape: a front page (90% identical), a DB proxy (repeated patterns), a service behind a cache (mostly unique).

## You will learn

- Reconstruct counts and percentiles from sampled data
- Implement consistent sampling for traces
- Choose per-key, target-rate, head, tail or buffered sampling

## Claims and numbers

| Figure | Context |
|---|---|
| 1/1000 vs 1/10 | Child vs parent rates without orphans |
| 30 s | Recent-volume window example |
| 500 ms | Outlier latency threshold in examples |

## Terms

| Term | Meaning |
|---|---|
| Sample rate | How many real events one kept event represents |
| Consistent sampling | Same keep/drop decision across services for a trace |
| Target-rate sampling | Adjust rate to keep N events/s |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| dynsampler-go | Go library for dynamic per-key sampling | ADOT tail_sampling policies |
| Refinery | Honeycomb's tail-sampling proxy | ADOT gateway |

## Interview line

> I sample by key with target rates: errors and slow requests are always kept, noisy successes are squeezed, and health checks never kept. The rate travels on every event so counts and percentiles can be rebuilt. Trace decisions hash the trace ID so traces stay whole.

## AWS mapping

- ADOT Collector tail_sampling (status_code, latency, probabilistic, rate_limiting policies)
- X-Ray sampling rules for head sampling

## Practice question

**Q.** Why put sample_rate on every event instead of configuring it in the backend?

**Model answer.** Rates change: dynamically, per key, per service, at runtime. Only a rate attached to the event tells the backend how many events each one stands for. That lets you rebuild counts, sums and percentiles correctly even when rates vary.

## Exercise

Run pocs/05_sampling; add a key that never samples /healthz and verify the weighted counts.

## Takeaways

- Sample everything, record the rate
- Consistency by trace ID
- Rare and bad things get their own budget
