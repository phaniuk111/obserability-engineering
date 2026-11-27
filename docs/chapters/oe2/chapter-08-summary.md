# Chapter 8: Getting started with observability analysis

Part 3: Analysis workflows. Coverage: Read in full from the book; text paraphrased.

## Summary

Debugging from known conditions relies on scar tissue: seniors who know which dashboard to check. Runbooks rarely keep up, because modern systems seldom fail the same way twice.

Debugging from first principles uses the core analysis loop. What are you trying to understand? Visualise the anomaly. Find the dimensions common inside the anomaly but not in the baseline. Filter and repeat until it's explained. Anyone curious can do this.

The brute-force part (diffing every dimension inside vs outside the selection) is what computers are good at. In a real Honeycomb incident, us-east-1a showed up in 98% of slow events vs 17% of baseline: a cloud-provider AZ problem nobody had announced.

## Key ideas

- Keep these in a runbook: owner, on-call, escalation, dependencies, entry-point queries. Don't keep a catalogue of failures and fixes. Wrong docs are worse than none, and instrumentation is the best documentation.
- Better telemetry alone doesn't stop you debugging from known conditions (tail -f | grep, flipping dashboards). The analysis method matters.
- Copilot: you steer (chat with stack traces). Commander: you set goals, the agent uses tools (Claude Code, Cursor). Caretaker: autonomous, e.g. posts three hypotheses when an alert fires. Errors compound as autonomy grows, and humans still own the outcome.
- Agents are optimised for confidence. A field called slow_request (true when >300 ms) was read as the cause. A one-line description fixed it.

## You will learn

- Run the core analysis loop on a latency spike
- Explain how BubbleUp-style automation works
- Place AI agents as copilot, commander or caretaker

## Claims and numbers

| Figure | Context |
|---|---|
| 98% vs 17% | us-east-1a share in slow events vs baseline |
| 2017 | Gartner coins AIOps |

## Terms

| Term | Meaning |
|---|---|
| Debugging from first principles | Treat understanding as provisional until the data proves it |
| Copilot / commander / caretaker | Agent autonomy levels |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Core analysis loop | Hypothesis-driven, iterative slicing | n/a (method) |
| BubbleUp | Automated baseline vs selection diff | CloudWatch Contributor Insights (top-N only) |
| AIOps (Gartner 2017) | ML for alert noise/anomaly | Amazon DevOps Guru; CloudWatch anomaly detection |

## Interview line

> I don't start from a guess. I box the anomaly, diff every dimension against the baseline, take the strongest, filter, and repeat. It works on systems I've never seen, and it's automatable.

## AWS mapping

- Athena/Logs Insights: compare `count(*) by field` inside vs outside a time/latency window
- DevOps Guru for anomaly hints (not a replacement)

## Practice question

**Q.** Walk me through debugging a P99 spike on a service you don't know.

**Model answer.** Confirm it on a heatmap and box the slow band. Compare its dimensions with the baseline: endpoint, build, region, AZ, customer, flags, instance type. Take the most over-represented value, filter, and repeat until a combination explains it. Then pull an exemplar trace to see where the time goes, and only then open code or a profiler.

## Exercise

Lab 3: switch the fault on and run the BubbleUp query. Then change the fault so it needs two attributes at once and see whether the query still surfaces it.

## Takeaways

- Method beats memory
- Automate the diffing; humans interpret
- Describe your fields for humans and agents

## Hands-on

[Lab 3: Find the culprit without a hypothesis](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/03-core-analysis-loop.md)
