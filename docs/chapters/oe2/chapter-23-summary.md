# Chapter 23: Learning speed is the constraint: letter to CTOs

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

In the AI era, delivery isn't limited by writing code. It's limited by how fast you can validate, understand and learn. Unpaid sociotechnical debt is the biggest drag. AI doesn't remove the need for engineering discipline; it removes the excuses for not having it.

The three debts. Developers live in tests, not reality: only ops has production in its loop. Telemetry is treated as infrastructure, not product: orgs went broad instead of deep. Developer tools were never designed as products: 'add good telemetry' is a maze.

Boris Tane's framing: the old wide SDLC collapses into intent → build → observe → repeat. Observability is the only quality gate that survives, and context is what's left.

## Key ideas

- A Gartner reference customer went from $50k/yr on monitoring (2009) to $24M/yr on 'observability' (2024): 48% a year for 15 years. Observability takes 20–30% of infra spend.
- Tests: does a Friday shipper know by Monday how it performed? Do incidents take 15 minutes with the rockstar and 45 without? Can a new hire instrument a service without pinging three people?
- DORA 2025: AI amplifies whatever you already have, whether strong feedback loops or chaos.
- Shifts: match tools to architecture; run observability as a platform product; treat product observability as an investment. Observability inherits the properties of the code it observes.
- Measure: time from deploy to validated understanding; share of incidents found internally vs by customers; share of deploys with a post-deploy check.
- Darragh Curran (Fin CTO): shipping is your heartbeat; understanding is your breathing.

## You will learn

- Name the three sociotechnical debts
- Explain why AI amplifies existing behaviour
- Measure whether the shift is working

## Claims and numbers

| Figure | Context |
|---|---|
| $50k → $24M | Gartner customer 2009 → 2024 |
| 48%/yr | Spend growth for 15 years |
| 15 vs 45 min | Incident time with/without the rockstar |

## Terms

| Term | Meaning |
|---|---|
| Sociotechnical debt | Hidden cost of misaligned culture/process and technology |
| Paved path | Default workflow that makes the right thing easy |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Sociotechnical debt (Tamburri & Di Nitto 2015) | Misalignment of social and technical structures | n/a |
| DORA 2025 | AI amplifies existing practices | n/a |
| Platform engineering | Product thinking for internal developer tools | Backstage on AWS (Harmonix); AWS Proton support ended Oct 2026 |

## Interview line

> With AI, generating code is cheap and confidence is expensive. I'd invest in the developer-to-production feedback loop and measure time from deploy to validated impact, not dashboard counts.

## AWS mapping

- Platform paved path: ADOT auto-instrumentation via EKS add-on + standard resource attributes + golden queries

## Practice question

**Q.** As a new head of platform, you have one quarter. What do you do about observability?

**Model answer.** Run three tests: can devs validate a Friday deploy by Monday, does incident resolution depend on specific people, can a new hire instrument a service alone. Pick one critical domain and instrument it deeply. Ship a paved path (library + defaults + golden queries). Report deploy-to-understanding time and the share of incidents found internally.

## Exercise

Answer the three diagnostic questions for your org with evidence.

## Takeaways

- Learning speed is the constraint
- Debts get called in at AI speed
- Measure deploy → understanding

## Since the book (checked against documentation, 2026-11-27)

- AWS Proton support ended on 7 October 2026; AWS's migration guide points to Backstage-based options such as Harmonix.
