# Chapter 4: Getting started with instrumentation

Part 2: Instrumentation fundamentals. Coverage: Read in full from the book; text paraphrased.

## Summary

Instrumentation is code you add so your app reports what it's doing. Without it, you add log lines after the incident and wait for it to happen again.

OpenTelemetry separates the API in your code from the destination in config. The API does nothing until it's configured, so library authors can call it safely. Auto-instrumentation gives you the skeleton (HTTP, DB, RPC calls). Custom instrumentation adds the muscle: business logic, domain errors, user context.

The engineers who write the code should own its instrumentation. A platform team supplies conventions, libraries and review guidelines. Treat instrumentation as a deliverable, like tests.

## Key ideas

- Start custom instrumentation from critical user journeys: registration, search, cart and checkout for e-commerce. Capture domain errors such as 'insufficient inventory', and tag them temporary or permanent, actionable or not.
- Ask: which users are affected? What are the key pipeline stages? Which flags were on? Then add why-context: segment, active flags, request source.
- Auto-instrumentation can drown you. In production, spans for every DB or Redis call can cost real performance. Customising means taking away too.
- Write instrumentation backend-agnostic and leave processing (drop, transform, PII filtering) to the pipeline. Removing data later is easier than wishing you'd captured it.
- Hidden costs: 10–15 tools means cognitive overload and slower incidents, plus time spent working out why spans were sampled, and cross-AZ egress when you self-host.
- Metrics are a form of sampling (pre-aggregation). Head sampling at 1% will probably miss an error that happens 0.1% of the time, and it can't know a downstream call will fail. Tail sampling buffers the whole trace before deciding.

## You will learn

- Explain auto vs custom instrumentation and why you need both
- Build a custom instrumentation strategy from critical user journeys
- Compare head and tail sampling and their failure modes

## Claims and numbers

| Figure | Context |
|---|---|
| 1% / 0.1% | A 0.1% error is likely missed by 1% head sampling |
| 10–15 tools | Scattered data, hidden cognitive cost |

## Terms

| Term | Meaning |
|---|---|
| Auto-instrumentation | Library/framework hooks that emit telemetry without code |
| Custom instrumentation | Hand-added business context and spans |
| Head sampling | Keep/drop decided at the start of a trace |
| Tail sampling | Decision after buffering the whole trace |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| OpenTelemetry (OTel) | Vendor-neutral APIs/SDKs/Collector | AWS Distro for OpenTelemetry (ADOT) |
| Head vs tail sampling | Decide at trace start vs after the whole trace | X-Ray sampling rules vs ADOT tail_sampling |

## Interview line

> I use auto-instrumentation for coverage and custom instrumentation for the business: journeys, domain errors, user and flag context. I sample everything, and use tail sampling so errors and slow traces are always kept.

## AWS mapping

- ADOT Collector as agent (DaemonSet) + gateway
- X-Ray for traces, or export OTLP to a vendor

## Practice question

**Q.** Head sampling at 1% on a service doing 10k req/min. A rare error affects 0.1% of requests. What happens, and what do you do?

**Model answer.** About 10 errors a minute, and roughly 0.1 of them gets kept, so they're mostly invisible and the downstream outcome isn't known at decision time. I'd switch to tail sampling at a gateway (keep every error and slow trace, sample the rest consistently by trace ID), and record the sample rate on each event so counts can be rebuilt.

## Exercise

Pick one journey in your system. List its start/end points, five context attributes and three domain errors to capture.

## Takeaways

- Auto + custom, always
- Owners instrument; platforms enable
- Sample everything, but tail-sample what matters
