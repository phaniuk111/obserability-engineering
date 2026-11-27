# Chapter 31: Instrumentation for observability teams

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

An observability team's north star is to define and look after the organisation's shared telemetry language. You may not write most instrumentation, but you are judged on how well everyone else does. That means owning the frameworks, pipeline configuration, alerting infrastructure and SLO tooling.

OpenTelemetry's semantic conventions are the shared vocabulary (names such as `http.request.method`) and grammar (dot-separated namespaces from general to specific, client/server and producer/consumer roles). A telemetry schema treats what a service emits like a versioned API contract that tools can lint, generate code from and check at runtime.

Adoption does not come from a wiki page or from dashboards handed over as a done deal. It comes from paved paths: the correct route should also be the quickest one, and its entry point should sit where engineers already look.

## Key ideas

- Schema-writing rules. Start from the questions people ask. Put truly organisation-wide identifiers at a high namespace level (`acme.transaction.id`, not `acme.<service>.transaction.id`), because mixed identifiers give wrong joins and AI assistants will not notice. Model actors and roles rather than protocols. Keep one meaning per key across signals.
- Keep high-cardinality ids (transaction, user) on spans and events, and put a low-cardinality cousin (`customer.region`, tier) on metrics so you can still move between signals.
- Don't wrap the OTel API or rename its methods. Extend it (a decorator that starts a span and updates metrics) or re-export it from one internal package so many services migrate without changing callers.
- Hide the right complexity: SDK setup becomes a one-liner in the service framework. Context propagation trips most teams up, so build it into the RPC framework; adoption then means upgrading an internal library.
- Build your own Collector distribution with the OpenTelemetry Collector Builder (OCB) and small custom components rather than squeezing everything into config: fewer resources, smaller attack surface, more control.
- Weaver in CI and at deploy time live-checks emitted telemetry against the registered schema. In regulated firms the same run is evidence for auditors that no sensitive field leaks. An agent can take Weaver's findings plus the code and propose fixes.
- Dapper story: tracing adoption at Google stalled until the team added a single link from the graphs engineers already opened when paged. Usage doubled, then tripled.
- Make adoption safe: dual-send to cheap blob storage and the telemetry database (especially when changing sampling), drop high-cardinality attributes from metrics in the pipeline, ship a default local pipeline so developers can see what they emit, and manage pipeline config centrally so it is clear why data was dropped.
- Sampling frustrates people when expected data is missing. Start simple, keep rates easy to explain, begin with too much data and walk it back.
- Regulated environments: compliance is about the evidence you can show, security is about the isolation you guarantee, and observability's strength is correlation, which cuts against both. Consistent one-way hashing or tokenisation of identifiers keeps correlation without exposing the value.
- Use compliance tiers: let teams experiment quickly in lower environments and graduate services upward. Moving tooling earlier is not enough; developers need the benefit earlier too. Frame the work as making compliance evidence easier to collect.
- Minimum capabilities there: vendor management, encryption (mTLS between every component, plus at rest), and multilayer data analysis (prove what every byte sent anywhere contains). Then chargeback, schema control, proxies you control, tokenisation, and short-lived attested credentials.
- Earlier attempts at one telemetry dialect (the Microsoft stack, Java, Unix) each fitted their own world and generalised poorly; that is the gap semantic conventions fill.

## You will learn

- State what an observability team should own
- Use semantic conventions and telemetry schemas as a contract
- Drive OTel adoption with paved paths, including in regulated environments

## Claims and numbers

| Figure | Context |
|---|---|
| 2x then 3x | Dapper usage after adding one link |
| 12 months | Typical path to production in regulated industries |
| 2 heuristics | Namespaces go general → specific; actors are client/server or producer/consumer |

## Terms

| Term | Meaning |
|---|---|
| Paved path | The default route that makes the right thing the easy thing |
| Live check | Comparing emitted telemetry with the registered schema |
| Tokenisation | Replacing a sensitive value with a stable stand-in |
| Compliance tier | A level of controls an environment must meet |
| Chargeback | Billing telemetry cost to the team that produces it |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Semantic conventions (semconv) | OTel's shared attribute names and structure | ADOT emits them; Application Signals reads them |
| Telemetry schema | Versioned, machine-readable description of what a service emits | n/a |
| Weaver | OTel tool to define, lint, generate from and live-check schemas | Run in CodeBuild/GitHub Actions |
| OCB (Collector Builder) | Builds a custom Collector distribution from a manifest | ADOT is AWS's distribution |
| Dapper | Google's internal tracing system | X-Ray lineage |
| mTLS | Mutual TLS between components | ACM Private CA; VPC Lattice / service mesh |
| FIPS 140-2 | US crypto module standard often demanded as evidence | AWS FIPS endpoints |
| Hazel Weakly, Austin Parker | Chapter authors | n/a |

## Interview line

> I treat telemetry like an API: a schema in the repo, linted in CI, with shared names from OTel semantic conventions. Then I make adoption a library upgrade, with propagation built into the framework and a link from the dashboards people already use.

## AWS mapping

- ADOT SDK/Collector as the paved path on EKS/ECS/Lambda; a shared internal package wraps setup
- Pipeline guardrails in the Collector: hash ids, drop high-cardinality metric attributes, dual-send to S3
- Regulated: mTLS everywhere, KMS at rest, SigV4 to CloudWatch OTLP endpoints, Weaver output stored as audit evidence

## Practice question

**Q.** Teams ignore your OpenTelemetry rollout. What do you change?

**Model answer.** Find where engineers already look when paged and link from there into the new data. Make adoption a dependency upgrade: propagation and setup live in the service framework with sensible defaults, so the correct route is also the quickest. Publish a small schema for shared business identifiers and lint it in CI with Weaver instead of asking people to read a naming wiki. Make it safe: dual-send to cheap storage, simple sampling, a local pipeline so developers see their own telemetry. Then publicise wins from the teams in the most pain.

## Exercise

Write a ten-attribute schema for one service: five from OTel semantic conventions, five business attributes under your company namespace. Mark which may appear on metrics.

## Takeaways

- Own the shared telemetry language
- Schema as contract, checked in CI
- Correct route = quickest route

## Hands-on

[Lab 6: The pipeline](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/06-pipeline.md)

## Since the book (checked against documentation, 2026-11-27)

- The chapter's examples use `db.system`; current convention docs use `db.system.name`. A schema check in CI is what catches this kind of drift.

## Official documentation

- [Build a custom Collector (OCB)](https://opentelemetry.io/docs/collector/extend/ocb/): Your own distribution from a manifest
- [Observability by design with Weaver](https://opentelemetry.io/blog/2025/otel-weaver/): Registry check, code generation, live check
- [Collector management with OpAMP](https://opentelemetry.io/docs/collector/management/): Central control of Collector config
