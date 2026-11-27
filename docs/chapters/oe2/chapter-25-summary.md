# Chapter 25: The landscape through a systems lens

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

Most orgs run a fast but isolated dev loop (build, test, merge, move on) and a slow, reactive ops loop (alert, investigate, fix). Neither connects 'I wrote this' to 'I can see what it did'.

The value loop is build → deploy → observe → learn. Fin ships its Ruby monolith about 70 times a day, 8–15 minutes from merge to full rollout. Deploying without looking is an open loop.

Why closing it is rare: the economics of cognitive load. Without precision data, looking isn't worth it, so nobody looks, so the tools never improve. AI breaks the stalemate.

## Key ideas

- Precision means something like: 'for requests on build X with flags Y, test users on the 10% canary vs the 90% baseline, compaction rate for long strings rose 5% and disk use fell 30%; status codes unchanged.' 'No spike in errors' isn't precise.
- Three pillars suits operational outcomes and infrastructure. Unified storage suits developer learning: e.g. all EU mobile users with flag X who hit errors in checkout.
- AI makes code nearly free; the constraint is coherence. Most code is brownfield or blackfield. Agents can check back on slow burns, and continuous-review agents can flag risky changes.
- Most orgs spend on the goalie (ops) and leave the field empty. Decide which loop is your bottleneck before running vendor bake-offs.

## You will learn

- Contrast dev, ops and value-creation loops
- Map three pillars and unified models to the loops they serve
- Choose a starting point by bottleneck

## Claims and numbers

| Figure | Context |
|---|---|
| ~70/day | Fin deploys |
| 8–15 min | Merge to full rollout at Fin |
| up to 1/3 | Infra spend on observability in some companies |

## Terms

| Term | Meaning |
|---|---|
| Value creation loop | Build → deploy → observe → learn |
| Open loop | Acting without observing the result |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Inner / outer loop | Dev iteration / production operations | n/a |
| Blackfield | Chaotic brownfield code | n/a |

## Interview line

> I'd ask which loop is our bottleneck. If it's stability, mature three-pillars tooling is fine. If it's delivery speed or AI-generated code nobody understands, invest in the developer learning loop and unified data.

## AWS mapping

- Ops loop: CloudWatch alarms/SLOs into your paging tool (Systems Manager Incident Manager is on AWS's maintenance list)
- Dev loop: deploy event → pre-filtered cohort comparison link to the author

## Practice question

**Q.** How would you prove to a skeptic that the dev loop matters more than another dashboard?

**Model answer.** Show the gap: how long after merge before anyone looks at a change, and what share of issues customers find first. Then pilot on one service. Auto-link each deploy to a canary-vs-baseline view and measure how many regressions are caught before customers notice.

## Exercise

Measure your merge → first look interval for the last 10 PRs.

## Takeaways

- The missing loop is where value is learned
- Pick tools by loop, not features
- Don't overspend on the goalie
