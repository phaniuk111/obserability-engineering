# Chapter 22: Case study: Fin

Part 5: Use cases. Coverage: Read in full from the book; text paraphrased.

## Summary

Fin (formerly Intercom) charges per resolved conversation, so resolution rate is the north star. It has risen about 1 point a month since March 2023, from dozens of stacked A/B tests. Hundreds of engineers in 20 teams ship about 100 changes a day.

When customers said Fin was slow, component speedups didn't help. They defined time to first token, measured on the frontend, and rebuilt traces with low-level spans showing where control passes between transactions. That revealed the critical path.

Eager requests (start the LLM work in parallel with pre-processing) cut 2 s from median TTFT. But conversations routed to humans wasted that LLM spend, which finance found in a quarterly margin review. Fix: cost per interaction on every trace, with its own SLO.

## Key ideas

- Latency is protected with an event-based SLO: percentage of interactions faster than the new baseline. Thresholds were too noisy given model provider variability.
- The warehouse query for LLM waste took minutes and refreshed daily: fine for finance, useless for engineers shipping 100 changes a day.
- Rasmussen's boundaries: acceptable performance (customers), economic failure (margins), unacceptable workload (engineers). Observability's job is to show operators where they stand against all three, in real time and linked to traces.
- The 'last mile' is empathy for customers, the business and engineers. Without it, observability is just a logging-cluster cost.

## You will learn

- Tie engineering to a customer metric and a business metric
- Find the critical path in async agent systems
- Use the Rasmussen boundaries to frame observability

## Claims and numbers

| Figure | Context |
|---|---|
| ~1 pt/month | Resolution rate growth since Mar 2023 |
| ~100/day | Changes shipped |
| 20 teams | Engineering teams touching Fin |
| −2 s | Median TTFT from eager requests |

## Terms

| Term | Meaning |
|---|---|
| Resolution rate | Share of conversations Fin resolves |
| Last mile of observability | Connecting signals to customer and business outcomes |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Time to first token (TTFT) | Submit → first rendered token | CloudWatch RUM custom metric |
| Rasmussen safety model | Drift toward failure within three boundaries | n/a |
| Eager/speculative requests | Start likely work before it's confirmed | Step Functions parallel state |

## Interview line

> Pick one customer signal (TTFT) and one business signal (cost per interaction), put both on the same detailed traces, and set SLOs on each. Speed gains that quietly burn margin show up the same day, not the next quarter.

## AWS mapping

- RUM for TTFT; X-Ray/ADOT spans with cost attribute; Application Signals SLOs on both

## Practice question

**Q.** You added speculative LLM calls to cut latency. What could go wrong, and how do you catch it?

**Model answer.** Wasted work when the speculation isn't used: cost rises without any latency signal, because those paths emit no latency metric. Catch it by putting cost per interaction (including discarded speculative calls) on traces with an SLO, and by tracking the speculation hit rate.

## Exercise

Define one customer-centric and one business-centric signal for your product and the trace attribute for each.

## Takeaways

- Measure what customers feel, end to end
- Put cost on the trace
- Watch all three Rasmussen boundaries
