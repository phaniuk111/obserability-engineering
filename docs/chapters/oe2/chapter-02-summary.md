# Chapter 2: How code crosses over into production

Part 1: Introduction to observability. Coverage: Read in full from the book; text paraphrased.

## Summary

Deploys aren't a switch from dev to ops. They're a process of building confidence, and they should be boring.

Durable code changes in small diffs against a baseline you trust, because its commitments live only in the code. Disposable code is regenerated instead of maintained. When disposable code becomes load-bearing, treat it as durable: tests, review, instrumentation, SLOs.

Six practices form a flywheel. 0: rich data and precision tooling. 1: a dev-to-prod feedback loop. 2: tests before deploy. 3: instrument and validate in prod. 4: separate deploys from releases with feature flags. 5: progressive delivery and automated rollbacks. Everything depends on practice 0.

## Key ideas

- Critical path compass: frequency, criticality, visibility, blast radius. Code is scaffolding, a post office (rare but core, like payroll) or a cathedral (constant, carries the business). Anything that can take down critical code is critical too.
- The closer code is to writing bits to disk, the more cautious you should be. Persistence mistakes can be permanent.
- Practice 1 gold standard: instrument as you write, autodeploy, then look at your change through that instrumentation before you forget what you meant it to do.
- Tests stop known problems from recurring. The bar: the only bugs you find in production are new ones. Expect more property-based, behavioural and characterization tests.
- Deploy is engineering's job; release is a product or marketing decision. One changeset per deploy. Batching 20 people's changes makes a breaking deploy about 20 times more likely.
- Canary failure story: fine at 1%, then every request queued on one DB row lock at 70%. Fix it in two ways: make every failure a new automated health check, and validate intent by comparing cohorts (new build vs old, one endpoint, one plan). That catches a 40% regression at 1% traffic.
- Bonus tools: capture/replay for DB upgrades, traffic splitters that diff old vs new APIs, strangler fig migrations.
- Critical-path stakes range from 'a newspaper headline tomorrow' to '$20 million lost per minute of delay at market open' to 'someone could die'. Effort should match.

## You will learn

- Explain durable vs disposable code and why maintenance sets the cost of software
- Walk through practices 0–5 of the test-in-prod flywheel
- Explain why canaries fail without precise observability, and how to fix it

## Claims and numbers

| Figure | Context |
|---|---|
| 1 week | Facebook early-2010s rollout: intern bake then 1% of a country |
| 20x | Likelihood one of 20 batched changes breaks the deploy |
| 40% slower | Regression detectable at 1% traffic with cohort comparison |

## Terms

| Term | Meaning |
|---|---|
| Durable code | Code maintained in place via small diffs; commitments live in the code |
| Disposable code | Code regenerated rather than maintained |
| Deploy vs release | Shipping an artifact vs changing user experience |
| Characterization test | Test that locks in current behaviour to protect expectations |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Blue-green / canary / rolling | Three progressive delivery variants | CodeDeploy deployment configs; ALB weighted target groups |
| Strangler fig (Martin Fowler) | Incremental rewrite around legacy code | API Gateway/ALB routing per path |
| DuckDB / Apache Iceberg | Columnar options for local trace analysis | Athena on Iceberg tables |
| MCP (Model Context Protocol) | Lets agents query telemetry from IDE/chat | Bedrock agents + tool APIs |

## Interview line

> I treat deploy and release as separate. Every merge auto-deploys behind a flag to a canary. I validate intent by comparing the canary cohort against the baseline on the exact endpoint and user tier I changed. Rollbacks are automatic, but only as trustworthy as the signal that triggers them.

## AWS mapping

- Flags: AWS AppConfig feature flags
- Progressive delivery: CodeDeploy canary/linear, Argo Rollouts on EKS
- Validation: CloudWatch Application Signals or a wide-event store grouped by deploy.build_id

## Practice question

**Q.** Your canary at 1% looked healthy, but the outage started at 70%. Why, and what would you change?

**Model answer.** Aggregate canary dashboards hide small, threshold and contention effects: lock contention, thundering herds, retries, unrepresentative samples, data corruption. I'd compare canary vs baseline per endpoint and cohort with high-cardinality data, step through more stages, and turn this failure into an automated health check so it can't happen the same way twice.

## Exercise

Sketch your service's critical path: label each component scaffolding, post office or cathedral, and note its blast radius.

## Takeaways

- Undeployed code ages like milk
- Flags + precise observability are worth more than the sum of the parts
- A rollback is only as trustworthy as its trigger
