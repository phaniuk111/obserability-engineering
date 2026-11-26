# Chapter 12: Acting on SLO burn alerts

Part 4: Technical deep dives. Coverage: Read in full from the book; text paraphrased.

## Summary

An error budget is how much failure the business tolerates. 99.9% is about 43 minutes a month, or a count of allowed bad events. Burn alerts forecast exhaustion so you act before the budget is gone. They work best up to about 99.95%.

Use a trailing 30-day window. Fixed calendar windows reset abruptly, while customers' memories don't. 90 days is too long: you could burn 90% of the budget in a day and still technically pass.

Predictive alerts project a baseline window forward. The rule of thumb: extrapolate at most 4x (the last hour predicts 4 hours; the last 6 hours predict 24). Run several lookaheads and act on whichever fires.

## Key ideas

- Threshold-crossing (alert at 30% left) just moves the goalpost and causes needless feature freezes.
- Relative burn: 10M req/month at 99.9% allows 10,000 failures. That's 2,880 fifteen-minute windows, so about 3.4 per window. A 4x alert fires past about 13 failures, 20x past about 68.
- Linear vs proportional: 25 of 50 units failing in a quiet 6 hours. Linear projects 100 more (fine). Proportional projects 50% of a normal day's 1,440 = 720 against a 438 budget, so page now.
- Context-aware alerts use the whole window (26 days of history plus 4 projected). They're expensive: Honeycomb's SLO evaluation hit over $5k a day in Lambda until they added caching.
- Time-sliced SLIs: if 94% of a minute's requests are under 300 ms, the whole minute is bad, about a quarter of a 4.38-minute four-nines budget. Event-based counts only the 6%. A 1% brownout at 99.99% behaves like a full outage at 99%: more than 7 hours of runway.
- Events let you backfill SLI changes and jump from a burning SLO straight to the failing requests.
- Lookahead examples: a regression trending 99.9% → 99.88% over a month can wait for the next business day; trending to 98% within an hour pages someone now.
- Short-term linear example: 50 failures in the last day projects 400 more over 8 days, 450 in total, which beats the 438 budget, so exhaustion in about 8 days.
- Context-aware example: the budget was 65% remaining when the one-day baseline began and 35% now. Burning 30% a day exhausts it well within the 4-day lookahead, so alert.
- Read the burn pattern before acting: a gradual steady burn (e.g. 51.4% left), bursts (31.4% left), or one big drop (down to 1.3%) point to different kinds of failure.

## You will learn

- Compute error budgets and burn projections by hand
- Compare threshold, relative and predictive burn alerts
- Explain why event-based SLIs beat time-sliced ones

## Claims and numbers

| Figure | Context |
|---|---|
| 43m50s | 99.9% per month |
| 8h45m57s | 99.9% per year |
| 21m54s | 99.95% per month |
| 4.38 min | 99.99% per month |
| $5,000/day | Lambda cost before caching SLO evaluation |
| 2,880 | 15-min windows in 30 days |
| 99.88% vs 98% | Ticket next business day vs page now |
| 51.4% / 31.4% / 1.3% | Gradual, bursty, one-off burn examples |

## Terms

| Term | Meaning |
|---|---|
| Error budget | Allowed bad events/time in the SLO window |
| Burn rate | Speed of budget consumption vs steady state |
| Lookahead / baseline | Projection horizon / data window used |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Site Reliability Workbook ch5 | Multiwindow burn-rate alerting | CloudWatch burn-rate alarms |
| Amazon CloudWatch 5-min default | Free tier metric granularity | Use 1-min or event-based |

## Interview line

> Sliding 30-day window, event-based SLI, two predictive burn alerts: a short one (1h baseline, 4h lookahead) that pages, and a long one (6h baseline, 24h lookahead) that files a ticket. I extrapolate proportionally to expected traffic, not raw counts.

## AWS mapping

- Application Signals SLO burn-rate alarms (short + long windows)
- EventBridge → PagerDuty for page; Jira for ticket

## Practice question

**Q.** 99% SLO, 43,800 units/month. Last 6h: 50 units, 25 failed. Page or not?

**Model answer.** Budget is 438. Linear says 100 more failures in 24h, which looks fine. But 50% of the units are failing during a quiet period. At normal volume (1,440/day) that's about 720 failures, so the budget is gone in roughly half a day. Page.

## Exercise

Run pocs/04_slo_burn; change the bad day's failures until the 4-day alert flips.

## Takeaways

- Forecast, don't wait for zero
- Baseline ≈ lookahead / 4
- Count events, not good minutes
