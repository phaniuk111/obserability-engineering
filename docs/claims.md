# Numbers to know

Check the book before quoting any figure in writing. Figures are as reported by the book (often from contributors, Gartner, or the authors' own systems).

## Curated

| Topic | Figure | Chapter |
|---|---|---|
| 99.9% budget | 43m50s/month; 8h45m57s/year (365.25-day year) | ch12 |
| 99.99% budget | ≈4.38 min/month | ch12 |
| Relative burn example | 10M req, 99.9%, 15-min windows → ~3.4 allowed; 4x ≈ 13, 20x ≈ 68 (exact 13.9 / 69.4) | ch12 |
| Dimensionality | 4 fields → 15 combos; 8 → 255; 30 → ~1.1B | ch1 |
| Average of averages | 183 ms naive vs ~175 ms weighted | ch5 |
| Spend | 20–30% of infra (ch3/ch23); 10–25% of infra bill and 2nd after cloud (ch27, Gartner); up to a third (ch25) | ch3, ch23, ch25, ch27 |
| Gartner customer | $50k (2009) → $24M (2024), 48%/yr for 15 years | ch23, ch29 |
| Retriever scale | 1.5 PB, >1B segments, 3–5M spans/s, 50 ms median / 5 s P99 | ch13 |
| ClickHouse node | 32c/128 GB ≈ 20B events/day; 300–400k/s peak; 10–20x compression | ch14 |
| Query Assistant | 25% → ~14% → <1% error rate | ch21 |
| Fin | ~70 deploys/day, 8–15 min each; resolution rate +~1 pt/month; −2 s TTFT | ch22, ch25 |
| Honeycomb builds | <15 min SLO (≤5% over); 7→14 min regression; target <7 min | ch18 |

## Per chapter

### ch01 What is observability?

| Figure | Context |
|---|---|
| 1960 | Kálmán coins observability |
| 1995 | Laprie's dependability framework |
| 30 fields | ≈1.1 billion field combinations |

### ch02 How code crosses over into production

| Figure | Context |
|---|---|
| 1 week | Facebook early-2010s rollout: intern bake then 1% of a country |
| 20x | Likelihood one of 20 batched changes breaks the deploy |
| 40% slower | Regression detectable at 1% traffic with cohort comparison |

### ch03 Origins of observability in software

| Figure | Context |
|---|---|
| 2016 | Honeycomb founded |
| 2019–2021 | Vendors rebranded monitoring as observability |
| 20–30% | Share of infra spend on observability at many companies |
| 10–20 | Typical number of observability tools (Gartner) |

### ch04 Getting started with instrumentation

| Figure | Context |
|---|---|
| 1% / 0.1% | A 0.1% error is likely missed by 1% head sampling |
| 10–15 tools | Scattered data, hidden cognitive cost |

### ch05 Structured events are the building blocks

| Figure | Context |
|---|---|
| 183 vs 175 ms | Naive vs correct cross-instance average |
| 1988 | SNMPv1 introduces the metric |
| 5 | Required span fields |

### ch06 Making structured events arbitrarily wide

| Figure | Context |
|---|---|
| 10%+ | Revenue share a single account can represent |
| hundreds | Attributes in a well-instrumented event |

### ch07 Instrumenting with OpenTelemetry

| Figure | Context |
|---|---|
| 100 x 2 ms | Symptom of too many spans |
| >100 | Receivers in the OTel Collector (ch16) |

### ch08 Getting started with observability analysis

| Figure | Context |
|---|---|
| 98% vs 17% | us-east-1a share in slow events vs baseline |
| 2017 | Gartner coins AIOps |

### ch09 Observability-driven development

| Figure | Context |
|---|---|
| 30–60 min | Page the merger after deploy |
| 3.4x / 5.5x | AI-coauthored commit size / net impact |

### ch10 AI agents for observability

| Figure | Context |
|---|---|
| 15 min | Mechanical incident groundwork agents can take |
| 2 s vs 5 s | Retry timeout vs upstream SLA in the example |

### ch11 SLOs for reliability

| Figure | Context |
|---|---|
| 12 weeks vs 12–18 months | ANZ launch vs estimate |
| <5 | User journeys used at ANZ launch |
| $23/min | Downtime cost at $1M/month |
| 99.99% ≈ 4.3 min/month | Four nines budget |

### ch12 Acting on SLO burn alerts

| Figure | Context |
|---|---|
| 43m50s | 99.9% per month |
| 8h45m57s | 99.9% per year |
| 21m54s | 99.95% per month |
| 4.38 min | 99.99% per month |
| $5,000/day | Lambda cost before caching SLO evaluation |
| 2,880 | 15-min windows in 30 days |
| 99.88% vs 98% | Ticket next business day vs page now |
| 51.4% / 31.4% / 1.3% | Gradual, bursty, one-off burn examples |

### ch13 Storage: Honeycomb's Retriever

| Figure | Context |
|---|---|
| 1 h / 250k / 1 GB | Segment finalisation thresholds |
| 76% | Dapper index size vs trace data |
| $5,000 vs <$50 | 1 TB RAM vs SSD |
| 1.5 PB | Retriever data (Nov 2025) |
| 3–5M/s | Spans ingested |
| 50 ms / 5 s | Median / P99 query |

### ch14 Storage: ClickHouse

| Figure | Context |
|---|---|
| 8,192 | Rows per granule (default) |
| 150 GB | Default max merged part size |
| 20:1 | Typical compression |
| 20B/day | Single 32-core node ingest |
| 300–400k/s | Peak events/s per node |
| 1.034 s / 1.78 s | P95/P99 of the slowest endpoint in Example 14-4 |
| 7.5 TB × 2 | NVMe pair ≈ 3 days before object storage |
| 500k/s | Events/s with write load-balancing |

### ch15 Cheap and accurate enough sampling

| Figure | Context |
|---|---|
| 1/1000 vs 1/10 | Child vs parent rates without orphans |
| 30 s | Recent-volume window example |
| 500 ms | Outlier latency threshold in examples |

### ch16 Telemetry pipelines

| Figure | Context |
|---|---|
| >100 | OTel Collector receivers |
| 20–40% | SIEM data never queried |
| 25,000+ | Collectors in one fleet |
| $2.6M | Overage eliminated |
| ~40% | Net savings after reinvesting 10% |

### ch17 Ontologies for humans and AI

| Figure | Context |
|---|---|
| ±$0.01 | Arithmetic tolerance |
| 0.6 | Example confidence floor |
| $20 vs $0.50 | Hallucinated vs simulated savings |

### ch18 Observability for CI/CD

| Figure | Context |
|---|---|
| 15 min / 5% | Honeycomb build SLO |
| 7 → 14 min | Median build 2018–19 |
| 10–20 → 100+ | PRs/week 2020–2025 |
| 3.5 GB | Data moved between steps |
| <7 min | Target that keeps devs watching |

### ch19 Mobile and frontend observability

| Figure | Context |
|---|---|
| >99.9% | Crash-free sessions in mature apps |
| 100M DAU × 1% | 1M users affected but invisible |
| 15 s | FSM checkout timeout example |

### ch20 Performance engineering

| Figure | Context |
|---|---|
| 17% | CPU in regexp.Compile |
| 5 lines | Size of the fix |
| ~30% | Arm price-performance gain per generation |
| 11 cores | Stranded per 32-core node |
| 25% | S3 reads share of Retriever serverless cost |
| 100 ms | Account for time to this granularity with spans |
| 40% vs 70–80% | Old SMT vs Arm utilisation targets |
| 5 MB/min | Profile size before compression |

### ch21 Observability for LLM applications

| Figure | Context |
|---|---|
| 25% → 14% → <1% | Query Assistant error rate |
| 90% | MCP server success SLO |
| 100 ms ≈ 1% sales | Amazon latency finding |
| 0.5 s → −20% traffic | Google 2006 finding |

### ch22 Case study: Fin

| Figure | Context |
|---|---|
| ~1 pt/month | Resolution rate growth since Mar 2023 |
| ~100/day | Changes shipped |
| 20 teams | Engineering teams touching Fin |
| −2 s | Median TTFT from eager requests |

### ch23 Learning speed is the constraint: letter to CTOs

| Figure | Context |
|---|---|
| $50k → $24M | Gartner customer 2009 → 2024 |
| 48%/yr | Spend growth for 15 years |
| 15 vs 45 min | Incident time with/without the rockstar |

### ch24 Systems thinking for software delivery

| Figure | Context |
|---|---|
| 60% vs 10% | Trace volume vs query share (example) |
| 500 GB | Per-load scan of an unused dashboard |
| 10,000x | Cardinality from adding user_id |
| $5k → $2M | Fraud queries vs incident caught |

### ch25 The landscape through a systems lens

| Figure | Context |
|---|---|
| ~70/day | Fin deploys |
| 8–15 min | Merge to full rollout at Fin |
| up to 1/3 | Infra spend on observability in some companies |

### ch26 The business case

| Figure | Context |
|---|---|
| 5 s / 85% | Honeycomb query target |
| 60 s / 99.95% | Data queryable target |
| 99.99% | Durability target |
| 100 ms ≈ 1% | Amazon sales per latency |
| +2%/s | Walmart conversion |
| +10% | Staples conversion from 1 s |

### ch27 Diagnosing your observability investment

| Figure | Context |
|---|---|
| ≥40%/yr | Spend growth for 15 years |
| 10–25% | Infra bill on observability |
| 50 saves | Goalie metaphor: defence failing |

### ch28 The organizational shift

| Figure | Context |
|---|---|
| 60–80% | Engineers who can investigate independently (modern) |
| <60 s | Arbitrary question answer time |
| 30% | War-room share of top engineers' time |
| 10% → 40% | Budget shift year 1 → year 3 |

### ch29 Build vs buy vs open source

| Figure | Context |
|---|---|
| >$10M | Cost to unwind the custom Apache module |
| ~$80k/month | Vendor quote in ELK example |
| >$2M/yr | Real cost of 'free' ELK |
| 358x | Cost growth at 48%/yr for 15 years |
| ~200 LOC / 2 weeks | Build-worthy OTel wrapper |
| 98–99.5% | Availability where self-hosted OSS may be fine |
| 18 months / $20M | In-house build promotion trap |

