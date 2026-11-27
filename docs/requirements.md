# Requirements checklist

What the book says a system or team should have in place. Use it as an assessment: tick what you can show evidence for.

| # | Requirement | Source | Lab |
|---|---|---|---|
| R1 | Services you write emit one wide structured event (or root span) per unit of work with build, flags, route, user/tenant, key timings | ch05, ch06 | Lab 2 |
| R2 | High-cardinality fields (user ID, build ID, trace ID) are queryable with no cardinality caps | ch01, ch13 | Lab 7 |
| R3 | Any field can be grouped/filtered at read time in seconds; no pre-declared indexes needed | ch03, ch13, ch28 | Lab 7 |
| R4 | Trace context propagates across HTTP, queues (links + correlation IDs) and async jobs | ch05, ch07 | Lab 1 |
| R5 | Instrumentation uses OTel APIs; vendor specifics live in Collector/distro config | ch04, ch07, ch29 |  |
| R6 | Telemetry naming follows semantic conventions and a checked-in schema; fields have descriptions | ch07, ch08, ch17, ch21 |  |
| R7 | Every deploy is linked to its author with a cohort comparison (new vs old build) within minutes | ch02, ch09, ch25, ch28 | Lab 3 |
| R8 | Deploys are decoupled from releases via feature flags; flag state is on every event | ch02, ch06 | Lab 2 |
| R9 | Progressive delivery with automated rollback driven by precise signals | ch02 |  |
| R10 | Paging is driven by event-based SLO burn alerts with ≥2 lookahead windows; unactionable alerts are deleted | ch11, ch12 | Lab 4 |
| R11 | Sampling records the rate on each event; errors/slow traces always kept; decisions consistent by trace ID | ch15 | Lab 5 |
| R12 | A pipeline tier redacts PII centrally, enriches, reduces and routes; buffers with backoff and backpressure | ch16, ch07 | Lab 6 |
| R13 | Telemetry fidelity is tiered by service criticality and adjustable without redeploys | ch27, ch29 | Lab 6 |
| R14 | Observability cost is attributed per team/service and visible to them | ch24, ch27, ch29 |  |
| R15 | CI/CD workflows are traced; build time SLO and flake rate tracked | ch18 |  |
| R16 | Profiles are collected continuously and can be tied to spans or customers | ch20 |  |
| R17 | Mobile/frontend measure intention → outcome and can pull targeted sessions | ch19 |  |
| R18 | AI features log model, prompt version, tokens, feedback; bad traces promote to evals; AI outputs validated by invariants | ch17, ch21 |  |
| R19 | An agent-readable context layer exists: topology, aliases, owners, deploys, incidents, business criticality | ch10 |  |
| R20 | 60–80% of engineers can investigate production independently; no 'two or three people' dependency | ch01, ch28 |  |
| R21 | Observability for product code reports to engineering and is run as a platform product | ch23, ch26, ch28 |  |
| R22 | Observability backend is operationally independent from production dependencies | ch13, ch29 |  |
| R23 | Tool evaluations start from written success criteria and run as a POC on real production load, with dual-written data | ch30 |  |
| R24 | Migrations have OKR milestones and a published date for decommissioning the old tool | ch30 |  |
| R25 | Shared business identifiers have one name in a company namespace; a schema check runs in CI | ch31, ch07 |  |
| R26 | Identifiers that raise compliance scope are consistently hashed or tokenised before storage | ch31, ch16 | Lab 6 |
| R27 | User-facing commitments exist outside the code as contracts, evals or SLOs that a rewrite can be checked against | ch32 | Lab 4 |
