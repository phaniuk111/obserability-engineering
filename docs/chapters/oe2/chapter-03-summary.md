# Chapter 3: Origins of observability in software

Part 1: Introduction to observability. Coverage: Read in full from the book; text paraphrased.

## Summary

Charity Majors tells the story. Using Scuba at Facebook (while working on Parse) made novel problems findable without prior knowledge, and junior engineers started out-debugging experts. Honeycomb (2016) tried to rebuild that experience from first principles.

They defined observability technically: understand any state, even a never-seen one, which needs high cardinality, high dimensionality, an explorable interface and trace views. Vendors rebranded monitoring between 2019 and 2021, and by the time Gartner added the category in 2022 the word meant anything.

Monitoring is your personal bank account: autopay and a balance check. Observability is running a bank: trace any transaction across millions of accounts, on demand. It costs more because it does more.

## Key ideas

- Six functional requirements: (1) wide events per unit of work, ideally hundreds of fields; (2) high cardinality, unique IDs welcome; (3) raw storage, read-time aggregation, all keys fast; (4) zoom from one request to the whole system and see traces; (5) exploratory UI not static dashboards; (6) queries return in seconds.
- Traditional tools handle known-unknowns. Observability handles unknown-unknowns, and also product quality and how users actually behave.
- Observability 1.0 (a tool per signal, correlations maintained by hand, data paid for many times) vs 2.0 (one store, pay once). Hazel Weakly proposed lakehouse as 3.0.
- Cost argument: Gartner says 10–20 observability tools is the norm, so you pay 10–20x per request. Observability is 20–30% of infra spend at many companies.
- AI moved the bottleneck from writing code to understanding it.
- In 2010 the typical stack was LAMP (Linux, Apache, MySQL, PHP), and monitoring plus dashboards worked. By 2026 there's no typical stack, and agents add nondeterminism.

## You will learn

- Tell the history briefly: DTrace, Scuba, Honeycomb, vendor rebranding
- Recite the six functional requirements
- Explain known-unknowns vs unknown-unknowns with the finance analogy

## Claims and numbers

| Figure | Context |
|---|---|
| 2016 | Honeycomb founded |
| 2019–2021 | Vendors rebranded monitoring as observability |
| 20–30% | Share of infra spend on observability at many companies |
| 10–20 | Typical number of observability tools (Gartner) |

## Terms

| Term | Meaning |
|---|---|
| Known-unknowns | Risks you know exist and can write checks for |
| Unknown-unknowns | Failures you couldn't anticipate |
| Observability 2.0 | Unified store of wide events; pay to store once |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Bryan Cantrill / DTrace (2003) | First 'software observability' deck | n/a |
| Scuba (Facebook) | In-memory event analytics that inspired Honeycomb | n/a |
| Observability 1.0/2.0/3.0 | Separate stores / unified store / lakehouse | CloudWatch silos vs S3+Iceberg lakehouse |
| Christine Yen | Honeycomb cofounder (analytics background) | n/a |
| LAMP | Linux, Apache, MySQL, PHP stack (2010 norm) | EC2 + RDS MySQL |

## Interview line

> Monitoring answers questions you predicted. Observability answers ones you didn't, because it keeps raw, high-cardinality events and aggregates at query time in seconds.

## AWS mapping

- Lakehouse-style observability: OTel → Firehose → S3 (Parquet/Iceberg) → Athena; or Amazon Managed Grafana on top

## Practice question

**Q.** An exec says 'we already have observability: we bought tool X.' How do you respond?

**Model answer.** I'd ask outcome questions. Can any engineer answer a new question in under a minute? Can we group by user ID or build ID without cardinality limits? Do we find issues before customers do? If not, we bought monitoring with a new label. Then I'd show it with a concrete question we can't answer today.

## Exercise

Score your current stack against the six requirements, 0–2 each, and note the lowest two.

## Takeaways

- Junior engineers out-debugging experts is the tell of real observability
- Labels are noisy; use the six requirements
- Cost multiplies with each silo
