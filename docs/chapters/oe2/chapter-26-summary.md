# Chapter 26: The business case

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

Start with which loop is the bottleneck, not vendor features. The operational loop is a safety net and a cost center: uptime, faster incident response, avoided outages, lower burnout. Fred Hebert's line: great firefighters should start reading the fire codes.

Developer learning loops are an investment. Many productivity tools fail to pay off because they don't close the loop: chaos engineering without attribution is just chaos, flags without validation are a trust fall, progressive delivery without detection is just a slower pipeline.

Observability inherits the properties of the code it observes. Infrastructure observability is a cost center; observability of revenue code is an investment; delivery tooling multiplies your biggest cost, engineers.

## Key ideas

- Signs of operational trouble: customers find bugs first, small incidents snowball, the investigation backlog grows, break/fix crowds out features, nobody will ship the AI diffs.
- External measures: differentiators and their SLOs. Honeycomb: builder queries under 5 s 85% of the time, deep queries under 30 s 85%, data queryable within 60 s 99.95% of the time, 99.99% durability. Amazon: 100 ms ≈ 1% of sales. Walmart: +2% conversion per second saved. Staples: +10% from a 1 s faster home page.
- Pivots found by watching users: Instagram (Burbn), YouTube (dating), Twitter (Odeo), Slack (a game's chat tool).
- Internal measures: uncertainty is expensive, and hiring adds coordination tax. Report developer observability into the VP Eng/CTO, not IT/ops, and staff it like a platform team.
- Finance-friendly terms: fully loaded engineering cost, capacity recovered from firefighting, time to market. Use conservative baselines.

## You will learn

- Build separate cases for operational vs developer loops
- Use external and internal measures
- Frame observability as investment vs cost center correctly

## Claims and numbers

| Figure | Context |
|---|---|
| 5 s / 85% | Honeycomb query target |
| 60 s / 99.95% | Data queryable target |
| 99.99% | Durability target |
| 100 ms ≈ 1% | Amazon sales per latency |
| +2%/s | Walmart conversion |
| +10% | Staples conversion from 1 s |

## Terms

| Term | Meaning |
|---|---|
| Cost center | Function with indirect value, managed to budget |
| Investment | Spend expected to compound |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| DORA / SPACE / DX | Developer productivity frameworks | n/a |
| Fred Hebert | Honeycomb SRE ('read the fire codes') | n/a |

## Interview line

> I split the case. Ops loop: uptime, MTTR, avoided outages, retention. Dev loop: deploy frequency, batch size, hypothesis-to-validation time, issues found internally. Then I tie each to a business metric the CFO already tracks.

## AWS mapping

- Tag-based cost allocation; observability spend per team via CUR tags

## Practice question

**Q.** Make the 60-second pitch to the CFO for a unified observability platform.

**Model answer.** Engineering salaries are our biggest cost, and we lose a large share to firefighting and slow validation. Faster validation means fewer regressions, faster releases and less war-room time. We'll measure it by deploy frequency, incidents found before customers, and hours recovered, against a conservative baseline. Infrastructure monitoring stays lean as a cost center.

## Exercise

List your product differentiators and the SLO and telemetry each needs.

## Takeaways

- Name the loop, then the case
- Cost centers get cut; investments get funded
- Report into engineering, run as a platform
