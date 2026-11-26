# Chapter 9: Observability-driven development

Part 3: Analysis workflows. Coverage: Read in full from the book; text paraphrased.

## Summary

TDD checks behaviour against a spec in a controlled, mocked world. ODD checks behaviour against reality. Production varies in ways tests strip out.

Observability works at the scale of systems, not functions. It narrows the search (which component, hop, cohort, build) and then you pick up a debugger or profiler. 'The telescope that aims the microscope.'

Every PR should answer: how will I know this is working as intended? Page the merger for 30–60 minutes after their deploy so they own the outcome.

## Key ideas

- Two paths from one latency spike: (a) trace a slow request, timeouts start at service3, reproduce locally with that context; (b) only write endpoints are slow, only some DB primaries, one instance type/AZ, so it's infrastructure, not code.
- In microservices the slowness could be code, a usage change, DB capacity, connection limits, the load balancer, service discovery, or a mix.
- Four questions after a deploy: is it doing what I expected, how does it compare with the last version, are people using it, is anything odd emerging?
- Teams that can't reason about production treat it as a glass castle and roll back by reflex. Accelerate showed speed and quality improve together. North Star metric: lead time to production. Cut batching. Put experienced engineers on the deploy pipeline.
- AI writes OTel easily but invents attributes and duplicates signals. Put explicit rules in agent config: spans are primary, attributes on root spans, layer don't duplicate, required route attributes with their sources. Honeycomb saw AI-coauthored commits 3.4x longer with 5.5x net impact.

## You will learn

- Contrast TDD and ODD
- Use observability as the telescope that aims the debugger
- Set AI instrumentation guidelines

## Claims and numbers

| Figure | Context |
|---|---|
| 30–60 min | Page the merger after deploy |
| 3.4x / 5.5x | AI-coauthored commit size / net impact |

## Terms

| Term | Meaning |
|---|---|
| ODD | Observability-driven development: ship features with the telemetry to verify them |
| Lead time to production | Code written → running in prod |
| Glass castle | Production so opaque teams fear touching it |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Accelerate (Forsgren, Humble, Kim 2018) | Speed and stability correlate | DORA metrics via CodePipeline/GitHub |
| GDB | Classic debugger | n/a |
| strace for microservices | Early name for observability | n/a |

## Interview line

> Tests tell me my code matches my assumptions. Observability tells me whether production agrees. I ship with the instrumentation that answers 'is it working?', and look while the intent is fresh.

## AWS mapping

- Deploy notifications to the merger via CodePipeline → EventBridge → Slack with a link to a pre-filtered query

## Practice question

**Q.** Your team rolls back by reflex at any blip. How do you change that?

**Model answer.** Reflex rollbacks come from not being able to tell a real regression from noise. Ship smaller changes behind flags, add canary-vs-baseline views per endpoint, and route post-deploy alerts to the author for an hour. Track lead time and change failure rate. Confidence grows as the signal improves.

## Exercise

Add 'How will I know this works in prod?' to your PR template and answer it for your last PR.

## Takeaways

- Instrument while intent is fresh
- Telescope then microscope
- Agents need explicit instrumentation rules
