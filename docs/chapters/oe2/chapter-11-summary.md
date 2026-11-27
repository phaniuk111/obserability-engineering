# Chapter 11: SLOs for reliability

Part 3: Analysis workflows. Coverage: Read in full from the book; text paraphrased.

## Summary

Alerts on CPU over 80% are potential-cause signals: maybe a backup, GC, or a circuit breaker. Teams learn to ignore them, which is normalization of deviance (a term from the Challenger investigation). Every postmortem then adds more.

Thresholds only cover known-unknowns. Distributed systems are mostly unknown-unknowns: cascading retries, partial brownouts, cache eviction churn. A helpful alert reliably means user experience is degraded, and it can be acted on systematically.

SLOs alert on symptoms of user pain (the what). Observability explains the why. Prefer event-based SLIs (each request good or bad) over time-based ones (each minute good or bad).

## Key ideas

- Event SLI example: eligible = POST /checkout, not kube-probe, root span; good = status < 400 and duration ≤ 4 s; ineligible events return null.
- Mat Vine (ANZ Bank) got launch-ready in 12 weeks against his 12–18 month estimate. Early standardised OTel with domain conventions removed weeks of regex work. They picked fewer than five user journeys. He's sceptical of piloting on a high-performing team (they rarely need SLOs) and targets stressed, critical teams. Full SDLC integration with hundreds of journeys still took 18 months.
- LLMs solve the blank page. Ask for a target with business context and the rationale, then push back. For $1M/month checkout: 99.99% ≈ 4.3 min/month ≈ $100 at risk, vs 99.9% ≈ 43 min ≈ $1,000. Don't out-SLO your dependencies.
- Check generated SLIs: models missed the root-span filter. Keep prompts in version control. Imperfect SLOs for many teams beat perfect ones for a few.
- Known-unknowns you can alert on: disk 95% full, queue depth over 70%, a TLS certificate expiring in 10 days, error rate over 10% for five minutes.
- When challenged on cost, the open-weights model revised five nines down to 99.95% (about 42 minutes a year, under $1k lost on ~$12M/yr). Pushing back on the first answer is part of the method.

## You will learn

- Explain why threshold alerts cause fatigue
- Define helpful alerts and event-based SLIs
- Roll out SLOs in an organisation; use LLMs to draft them

## Claims and numbers

| Figure | Context |
|---|---|
| 12 weeks vs 12–18 months | ANZ launch vs estimate |
| <5 | User journeys used at ANZ launch |
| $23/min | Downtime cost at $1M/month |
| 99.99% ≈ 4.3 min/month | Four nines budget |

## Terms

| Term | Meaning |
|---|---|
| SLI | Classifier of each eligible event as good/bad |
| SLO | Target proportion of good events over a window |
| SLA | External contract; looser than the SLO |
| Normalization of deviance | Ignoring alarms becomes normal |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Normalization of deviance | Accepting ignored alarms as normal (Challenger) | n/a |
| Google SRE book (2016) | SLO/SLI/error budget origin | CloudWatch Application Signals SLOs |
| Implementing SLOs (Hidalgo 2020) | Deep SLO reference | n/a |
| Ollama / gpt-oss-20b | Local open-weights model runner | Bedrock for hosted models |
| Google Customer Reliability Engineering (CRE) | Google programme teaching SLOs to customers | AWS Well-Architected reviews |

## Interview line

> I page on SLO burn, not CPU. An SLI classifies each eligible request as good or bad. The alert says users are hurting, and observability lets anyone find why. Unactionable alerts get deleted.

## AWS mapping

- CloudWatch Application Signals SLOs (request-based) + burn-rate alarms
- Exclude ELB/k8s health checks via user agent

## Practice question

**Q.** Pick an availability target for checkout doing $1M/month on one cloud region.

**Model answer.** About $23 a minute at risk. 99.9% allows about 43 minutes a month (~$1k); 99.99% about 4.3 minutes (~$100). 99.99% is achievable in one region with redundancy and roughly matches the managed services we depend on. 99.999% needs multi-region active-active, which costs more than it saves. I'd start at 99.9% measured on events, then tighten with data.

## Exercise

Lab 4: rewrite the SLI in `lab/clickhouse/queries/04_slo.sql` for another endpoint, with an explicit eligibility clause.

## Takeaways

- Alert on symptoms; debug causes with observability
- Event-based SLIs
- Roll out where pain is, not where teams already excel

## Hands-on

[Lab 4: SLOs and burn alerts](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/04-slo.md)

## Since the book (checked against documentation, 2026-11-27)

- Check the arithmetic in the chapter's LLM transcript: 99.95% availability allows about 4.4 hours of downtime a year (about 22 minutes a month), not the '~42 minutes' the model says. It makes the chapter's own point: treat the model as a draft generator and verify.
