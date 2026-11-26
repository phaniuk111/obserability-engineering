# Chapter 24: Systems thinking for software delivery

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

Software delivery is a sociotechnical system. Trist's principle: optimise the social and technical together. The weakest interventions (budgets, metrics, reorganisations) get absorbed. Changing information flows is far stronger, and observability is an information flow that creates feedback loops.

Amplifying loops become virtuous circles or death spirals: confidence (deploy more, smaller, faster MTTR), learning (answers lead to more questions), quality (clean baseline). Balancing loops need accurate signal to regulate, e.g. how many people join an incident, or observability spend.

What separates a virtuous circle from a death spiral is whether you can see well enough to correct yourself. Two teams breaking up a monolith with the same intent: the one with traces pauses at service eight; the other piles on services until it needs a rewrite.

## Key ideas

- Bad feedback: lossy (you double down on a change that hurt 0.5% of users), laggy (a Friday complaint about Tuesday's change, after 40 more changes), unpredictable (ingest gaps teach people to ignore intermittents), wrong (false alerts), missing (open loop: 'don't deploy Fridays').
- Workarounds become institutions: CABs, freeze windows, stale runbooks. That's theatrical safety, and standing still is falling behind.
- Observability of observability: e.g. checkout makes 60% of trace volume but gets 10% of queries; a dashboard scans 500 GB per load and nobody has opened it in 3 months; adding user_id multiplied cardinality 10,000x; $5k/month of fraud queries caught a $2M incident. Give teams budgets.
- Meadows' leverage points (subset, high to low): goals, self-organisation, rules, information flows, amplifying loops, balancing loops. People often push the right lever the wrong way: deploys hurt, so they added CABs and release trains.

## You will learn

- Explain amplifying vs balancing feedback loops with software examples
- Use Meadows' leverage points
- Diagnose lossy, laggy, unpredictable, wrong and missing feedback

## Claims and numbers

| Figure | Context |
|---|---|
| 60% vs 10% | Trace volume vs query share (example) |
| 500 GB | Per-load scan of an unused dashboard |
| 10,000x | Cardinality from adding user_id |
| $5k → $2M | Fraud queries vs incident caught |

## Terms

| Term | Meaning |
|---|---|
| Amplifying loop | Self-reinforcing cycle (flywheel or death spiral) |
| Balancing loop | Self-correcting cycle toward equilibrium |
| Leverage point | Place where small change shifts the whole system |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Trist principle (1981) | Jointly optimise social + technical | n/a |
| Donella Meadows, Thinking in Systems (2008) | Leverage points | n/a |
| Change Advisory Board | Approval gate; wrong-direction push | n/a |

## Interview line

> Observability is a leverage point because it changes what people can see, which changes many decisions every day. Without it, confidence loops run backwards: fewer, bigger, scarier deploys.

## AWS mapping

- Observability-of-observability: CUR + vendor usage APIs per team tag; budgets via AWS Budgets

## Practice question

**Q.** Your org banned Friday deploys and added a CAB after two outages. Respond.

**Model answer.** That's the right lever pushed the wrong way. Slower, bigger batches make failures more likely and harder to diagnose. Fix the feedback instead: smaller deploys behind flags, canary cohort comparison, automated rollback on SLO burn. Then remove the gates once evidence shows lower change failure rate.

## Exercise

Draw your deploy loop; mark where feedback is lossy, laggy or missing.

## Takeaways

- Change what people can see
- Self-correction separates virtuous from vicious cycles
- Measure the cost of observability itself
