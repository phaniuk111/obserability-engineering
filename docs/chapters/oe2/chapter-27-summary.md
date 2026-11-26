# Chapter 27: Diagnosing your observability investment

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

Gartner: observability spend has grown at least 40% a year for 15 years. It's the second-largest R&D software line after cloud, typically 10–25% of the infrastructure bill. Don't pay observability prices for monitoring outcomes.

The firefighting trap: if your goalie makes 50 saves a game, your defence isn't working. Cutting spend usually means less data, more blind spots, and higher costs later.

Activities aren't learning. Observability supplies the attribution, validation and detection that turn practices into learning.

## Key ideas

- Ops investment is working if: known causes are found faster, alert quality improves, escalations fall, recovery speeds up.
- Dev investment is working if: engineers answer novel questions, deploys get more frequent with smaller batches, more people debug, hypothesis-to-validation time shrinks, and more issues are found internally.
- Diagnostic questions: what share of spend fights fires vs prevents them? Does it build capabilities that move business metrics? Which feedback mechanism turns each practice into learning?
- Actions: cap each investment at diminishing returns, write impact statements, tier telemetry with feature-flagged verbosity (high/medium/low), attribute cost per request and give teams budgets.

## You will learn

- Answer 'cut observability spend' with a diagnosis
- Use loop-specific leading indicators
- Apply tiers, attribution and impact statements

## Claims and numbers

| Figure | Context |
|---|---|
| ≥40%/yr | Spend growth for 15 years |
| 10–25% | Infra bill on observability |
| 50 saves | Goalie metaphor: defence failing |

## Terms

| Term | Meaning |
|---|---|
| Tiered telemetry | Different fidelity per service criticality |
| Attribution | Tag cost/ownership on every request |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Impact statement | Full cost of an outage incl. churn, SLA penalties | n/a |

## Interview line

> When asked to cut, I first show what we buy. Then I tier: rich traces for revenue and active-development services, sampled traces for stable customer-facing ones, health checks for the rest. Every team sees its own spend.

## AWS mapping

- Tiering via ADOT config per namespace; AppConfig flags for verbosity

## Practice question

**Q.** Spend up 30%, nothing improved. What now?

**Model answer.** It isn't a communication problem. Check tool fit vs loop (are we paying observability prices for monitoring?), instrumentation quality and adoption. Check the leading indicators per loop. Then tier services, kill unqueried data, attribute cost to teams, and reinvest where it changes outcomes.

## Exercise

Classify your services into high/medium/low tiers with criteria.

## Takeaways

- Diagnose before cutting
- Indicators, not anecdotes
- Tier, attribute, budget
