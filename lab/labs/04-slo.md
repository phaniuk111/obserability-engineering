# Lab 4: SLOs and burn alerts (ch11, ch12)

**Goal:** define an SLI on events, compute budget and burn rate, and see a burn alert fire.

SLO for the lab: **99% of checkouts succeed within 500 ms.**

## Event-based, in SQL

`make fault-on`, wait a few minutes, then `make q F=04_slo`.

- **4a** classifies every checkout as good or bad and reports the SLI, the budget (1% of eligible events), how much of it is spent and the **burn rate**: bad ratio ÷ (1 − target). Burn rate 1 means you will use exactly the budget; in my run it was 4.3.
- **4b** is the same per minute, so you can see when it started.
- **4c** compares time-based and event-based accounting. A minute whose P95 is over 500 ms is a wholly bad minute in a time-based SLO. In my run that called 50% of minutes bad while 4.3% of requests were. Event-based SLIs measure what users experienced.

## On metrics, in Prometheus

`prometheus/rules.yml` builds the same idea from span metrics and uses the [SRE Workbook](https://sre.google/workbook/alerting-on-slos/) pattern: alert only when a long *and* a short window both exceed a burn-rate threshold (14.4 over 1 h and 5 min; 6 over 6 h and 30 min).

Open http://localhost:9090/alerts. `CheckoutLatencyBudgetBurnLab` (short windows, for the lab) goes pending, then firing, a few minutes after `make fault-on`, and clears after `make fault-off`.

Notice what the metrics version cannot do: "succeeds **and** is fast" needs two separate ratios, because a histogram bucket does not know which requests failed. On events it is one `WHERE` clause.

**Check yourself**

- 99.9% over 30 days allows how much downtime? (About 43 minutes.)
- Why two windows? (The long one shows it is significant; the short one shows it is still happening, so the alert stops when the problem does.)
- The book's own alerts project the budget forward instead ("will it run out within 4 hours?"). Same idea, different arithmetic.

**Try:** change the target to 99.9% in 4a. What happens to the burn rate?
