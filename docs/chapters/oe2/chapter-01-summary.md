# Chapter 1: What is observability?

Part 1: Introduction to observability. Coverage: Read in full from the book; text paraphrased.

## Summary

Kálmán coined observability in 1960 for control theory: can you infer a system's internal state from the outputs you measure? If the information was never captured, nothing recovers it later.

The authors now treat observability as a property of software dependability, next to Laprie's six (availability, reliability, maintainability, safety, confidentiality, integrity). Their seventh: the ability to understand or debug any system state, including ones you've never seen.

Two telemetry models collide. The three pillars store metrics, logs and traces in separate silos. That's right for infrastructure and third-party code you can't change. The unified model stores one wide, structured event (or span) per unit of work in a columnar store and aggregates at read time. That's right for code you write.

## Key ideas

- Monitoring tells you up/down and maybe where it's slow. You still need why. Cloud-era failures are mostly partial: slowness with no smoking gun.
- Qualitative test of how observable you are: do you detect faults before customers do, can you triage without an alert storm, and can any engineer (not only seniors) find why?
- Six principles of the unified model: context makes data combinatorially more valuable; details identify; pre-aggregation is one-way; you don't know what you don't know; static dashboards have limited value; fast feedback loops are everything.
- Dimensionality maths: 4 fields → 15 combinations, 8 → 255, 30 → about 1.1 billion (2^n − 1). Adding a 30th field adds as much as the first 29 together.
- With AI writing code and agents acting in production, telemetry becomes the last line of defence for checking that code does what was intended.
- One checkout request in three silos: metrics give only fleet aggregates (48,291 requests, P99 380 ms, 0.3% errors), logs give five timestamped lines, and the trace shows where the 142 ms went (89 ms in the cart query). No silo links them to this user or build.

## You will learn

- Define observability as a property of dependable software, not a tool category
- Explain cardinality and dimensionality with numbers
- Contrast the three pillars model with the unified storage model, and say when each is right

## Claims and numbers

| Figure | Context |
|---|---|
| 1960 | Kálmán coins observability |
| 1995 | Laprie's dependability framework |
| 30 fields | ≈1.1 billion field combinations |

## Terms

| Term | Meaning |
|---|---|
| Observability | Ability to understand or debug any system state from its outputs, including novel ones |
| Cardinality | Number of distinct values in a field (UUID = highest) |
| Dimensionality | Number of distinct fields/attributes on an event |
| Three pillars | Metrics, logs and traces stored in separate tools |
| Unified storage model | All telemetry stored once as wide structured events in a columnar store |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Rudolf E. Kálmán (1960) | Coined observability; dual of controllability | n/a |
| Jean-Claude Laprie (1995) | Six dependability properties | AWS Well-Architected reliability pillar is the closest framing |
| Canonical log line | One wide structured event per request/hop | CloudWatch Logs JSON + Logs Insights |

## Interview line

> Observability is how well you can explain any state of your system, even a brand-new one, from the telemetry it already emits, without shipping new code. Practically, that means wide, high-cardinality events you can slice at read time. Pre-aggregated metrics can't do that.

## AWS mapping

- Three pillars on AWS: CloudWatch Metrics + CloudWatch Logs + X-Ray, joined by hand
- Unified on AWS: OTel/ADOT wide spans → a columnar store (ClickHouse, Athena/Parquet on S3, or a vendor)

## Practice question

**Q.** Your dashboards are green but support reports slow checkouts. What does that tell you, and what would you change?

**Model answer.** It's a fault-detection gap. Aggregates are averaging away a cohort. I'd move checkout onto wide events with build ID, flags, region, plan and user ID, then compare the slow requests against the baseline. I'd also put an event-based SLO on checkout latency so customer pain pages us, not CPU.

## Exercise

Run pocs/01_wide_events: overall P99 looks fine, but the build × flag × region slice exposes a 6x slower cohort. Then compute 2^n − 1 for n = 4, 8, 30.

## Takeaways

- Observability is a property you build in, not a product you buy
- High cardinality is the point, not a problem
- Three pillars for infra; unified wide events for your own code
