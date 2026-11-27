# Chapter 6: Making structured events arbitrarily wide

Part 2: Instrumentation fundamentals. Coverage: Read in full from the book; text paraphrased.

## Summary

Jeremy Morrell (Cloudflare) walks through what goes on a wide event. A well-instrumented service has hundreds of attributes.

The families: service and infra metadata, build info, feature flags, runtime/library versions, HTTP and route details, timings and async rollups, errors, user and customer, rate limits, caching, localization, uptime, system metrics, and the domain fields only your business has.

Design events for the queries you'll run. If a slow auth step is only a child span, you need a self-join to group it by user type and region. Put auth.duration_ms on the main event and it's one GROUP BY.

## Key ideas

- Build info answers 'did something just deploy?': service.version, git hash, PR URL, diff URL, deployment trigger (merge, Slack bot, config change), deployment.age_minutes.
- A version breakdown showed a 500 spike during deploy came entirely from v1. The old version wasn't shutting down cleanly.
- Heatmaps reveal bimodal DB query counts and a few N+1 outliers that percentile lines hide.
- exception.slug is a unique, greppable literal per throw site. It's low-cardinality and jumps you to the code. A failed request without a slug shows a gap in error handling.
- Customer fields matter most. One account can be 10%+ of revenue. Also record impersonation (user.assumed, assumed_by) for audit.
- Use uptime_sec_log_10 so crash loops show up next to long-running instances. Cached system metrics on events are fine for debugging, but never alert on them.
- Mark wide events with main=true. Otherwise error rates double-count child spans that carry http.response.status_code.

## You will learn

- List the attribute families a mature wide event carries
- Explain why key timings go on the main span, not only child spans
- Use exception.slug and main=true conventions

## Claims and numbers

| Figure | Context |
|---|---|
| 10%+ | Revenue share a single account can represent |
| hundreds | Attributes in a well-instrumented event |

## Terms

| Term | Meaning |
|---|---|
| exception.slug | Unique greppable string per error throw site |
| main=true | Convention marking the wide event of a unit of work |
| deployment.age_minutes | Minutes since the running version deployed |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| BubbleUp | Honeycomb baseline-vs-selection diff | No direct AWS equivalent |
| Service catalog | Owner/team source of truth | AWS Service Catalog AppRegistry; Backstage |
| Heroku DYNO | PaaS instance id env var | ECS task ARN / Lambda request id |

## Interview line

> My main span per request carries everything needed to group without joins: build, flags, route, user tier, key timings, DB/HTTP call counts, a greppable error slug. Child spans are for the waterfall; the wide event is for analysis.

## AWS mapping

- Resource attributes from ADOT resourcedetection (ec2, ecs, eks)
- Build info injected via CodeBuild env vars into OTEL_RESOURCE_ATTRIBUTES

## Practice question

**Q.** An enterprise customer complains about being rate-limited. With wide events, how do you investigate in five minutes?

**Model answer.** Filter to their user.id/org.id, then do a heatmap of ratelimit.remaining grouped by http.route. If they suddenly hammered one endpoint, check user agent and source IP: buggy automation or leaked credentials. Then share ratelimit.limit and reset_at with them.

## Exercise

Write the wide-event schema for one of your endpoints: 30+ attributes grouped by family.

## Takeaways

- Hundreds of attributes is normal
- Design events for the queries you'll run
- Domain fields are the most valuable and only you can add them

## Hands-on

[Lab 1: Follow one request](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/01-traces.md)

## Since the book (checked against documentation, 2026-11-27)

- Trace flags are a bit field: only the lowest bit means 'sampled', and version `ff` is invalid. Trace Context Level 2 adds a 'random trace id' flag, so compare bits, not the string `01`.

## Official documentation

- [W3C Trace Context](https://www.w3.org/TR/trace-context/): The traceparent and tracestate headers, field by field
