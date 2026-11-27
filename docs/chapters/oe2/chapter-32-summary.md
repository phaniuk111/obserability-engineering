# Chapter 32: Where next: code as cache, developers in production

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

The first edition hoped developers would get good workflows in production. The verdict: mostly not yet. Developers still struggle to check the effect of a change they just shipped. The second edition makes one prediction: the line between dev and ops has to go, because the system developers build is production.

Why now: AI makes writing code cheap. Code used to be scarce, so we treated it as precious and trusted it because it had run for years. But the important things (what users expect, what we promised) were never written down. They live only in the code, which is why rewrites and migrations are so risky.

The way forward is to unbundle those commitments from the code: make them explicit as specifications, contracts and evaluations, and check them in production. Then code becomes a cache of current understanding that can be regenerated, the way immutable infrastructure made servers replaceable.

## Key ideas

- Chad Fowler's deletion test: if all the source vanished, what would you lose? Not the code, but knowledge: which behaviour is required, which failures are unacceptable, which invariants hold, how to tell a new version is correct, which bugs are deliberate fixes. Those are evaluation problems.
- The bottleneck has moved from generating code to validating it. The better question is not how to write safer code but what must exist so code can be replaced safely.
- What makes new code safe is the system around it (contracts, evals, monitoring, rollback), not the code's age. The real hazard is change nobody is watching.
- The infrastructure parallel: mutable, hand-tended servers drift. Being able to destroy and recreate a component is what makes it trustworthy. Honeycomb kills its oldest Kafka node on a schedule every Tuesday for that reason.
- Durability still matters once software meets users: people and other systems depend on stable behaviour. Free code does not make crossing from old to new cheaper; explicit, testable commitments behind interfaces do.
- The tools to extract commitments and treat architecture as the versioned artifact do not fully exist yet. The ideas do, mostly from ops and QA: behavioural tests, characterisation tests, capture/replay, traffic splitting.
- Start today: capture intent in instrumentation, follow it into production, and ask whether you, a colleague or an agent could confirm the change did what was meant.
- On the mood: fast change is disorienting, but there are precedents (weavers and the power loom, sysadmins and automation). Sysadmins mostly adapted by building the systems that replaced their manual work. The authors are sceptical of 'exponential forever' claims: growth curves flatten, and software was simply the easiest target because it is made of language and logic.

## You will learn

- Explain the book's one prediction and why AI makes it stick
- Describe what must exist before code can be regenerated safely
- Name practices you can start today

## Claims and numbers

| Figure | Context |
|---|---|
| 1 prediction | The dev/ops line must be destroyed |
| Every Tuesday | Honeycomb kills its oldest Kafka node |
| ~18x | Harder to sustain Moore's-law growth now than in 1971 (Becker) |
| 5 unknowns | What the deletion test exposes |

## Terms

| Term | Meaning |
|---|---|
| Code as cache | Code as a regenerable view of current understanding |
| Unbundling | Separating expectations and commitments from the implementation |
| Drift | Divergence caused by in-place change |
| Crossing over | Running old and new while honouring commitments to both (ch2) |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Chad Fowler, 'The Deletion Test' | Thought experiment about what is lost if code is deleted | n/a |
| Characterisation test | Records what a system does today so a rewrite can match it | n/a |
| Capture/replay, traffic splitting | Replay or mirror real traffic to a new version | VPC Traffic Mirroring; ALB weighted target groups; Lambda aliases |
| Immutable infrastructure | Replace, never patch in place | AMIs, containers, Auto Scaling instance refresh |
| Adam Becker, More Everything Forever | Source for the claim that exponential progress gets harder | n/a |

## Interview line

> When code is cheap to generate, the scarce thing is knowing a change is right. I'd put the commitments in specs, evals and SLOs, verify every deploy against production telemetry, and keep rollback one step away, so the implementation is replaceable.

## AWS mapping

- Progressive delivery with automatic rollback: CodeDeploy canaries or ALB weighted routing gated on CloudWatch alarms/SLOs
- Scheduled replacement as a habit: Auto Scaling instance refresh, node rotation on EKS, AWS Fault Injection Service experiments

## Practice question

**Q.** Your team wants to let agents rewrite a legacy service. What has to be true first?

**Model answer.** We need the commitments outside the code. That means contract and behavioural tests at the interface, characterisation tests or capture/replay of real traffic to pin current behaviour including odd edge cases, SLOs that state what users were promised, and instrumentation rich enough to compare old and new per customer and per endpoint. Then ship behind a flag or a traffic split, compare cohorts in production, and keep rollback immediate. Without those, new code is dangerous whoever wrote it; with them, the age of the code stops mattering.

## Exercise

Pick one service. List five commitments it keeps that are written nowhere except the code. For each, say what test, eval or SLO would make it explicit.

## Takeaways

- Validation is the bottleneck, not generation
- Move commitments out of the code
- Begin with observability in production
