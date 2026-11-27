# Chapter 19: Mobile and frontend observability

Part 5: Use cases. Coverage: Read in full from the book; text paraphrased.

## Summary

On devices you inherit the environment: thousands of models and OS versions, flaky networks, captive portals, ad blockers. Telemetry has to respect battery, bandwidth, privacy and cost. The status quo is crash reporting, RUM, CI benchmarks, and a separate product-analytics silo.

It's hard because workflows aren't auto-instrumentable. They span screens and threads with no shared context. Apps can't see the system around them. And telemetry is lost most often exactly when the app is struggling, which biases you toward false calm.

Matt Klein's approach: log everything to an on-device ring buffer that doesn't leave by default, and let a real-time control plane push rules saying what to send and when. Hanson Ho's: measure intention → outcome (checkout completion rate), detect user impact first, then find the app cause by cohort.

## Key ideas

- 1% of users at 2x slower may not move P50 or P99. At 100M DAU that's a million people.
- Mature apps exceed 99.9% crash-free sessions, so the leverage is in hangs, rage taps and functional bugs. Malformed JSON in a 200 OK can break the golden path while the server reports 99.99%.
- Klein's constraints: long release cycles, users who care about data, normal disconnection, unplanned termination, huge cardinality, and the main UI thread.
- Control-plane FSM example: on the checkout screen, if the user leaves or 15 s pass without checkout, count it and upload the session replay. You can target a cohort or a single user.
- P50 on mobile says little about the tail: a 1 s cold start on a new phone vs 10 s on a nine-year-old one.
- FakeBurger findings: Next button below the fold; a new discount-code format disabled Submit on first entry; rare errors hitting heavy users; many small glitches. Watch for adoption bias: early adopters have better phones.
- Classic mobile debugging story: NullPointerExceptions across several screens. RUM sessions ending in the crash all show a tap on a button whose label has non-ASCII characters, and a string assumption in that button's code is the bug.

## You will learn

- Explain why backend patterns fail on devices
- Design local ring buffer + control plane telemetry
- Measure UX as intention → outcome and debug by cohort

## Claims and numbers

| Figure | Context |
|---|---|
| >99.9% | Crash-free sessions in mature apps |
| 100M DAU × 1% | 1M users affected but invisible |
| 15 s | FSM checkout timeout example |

## Terms

| Term | Meaning |
|---|---|
| Fidelity dial | Remotely turn up/down what devices send |
| Intention → outcome | UX proxy: share of started goals completed |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| RUM | Real user monitoring of client events | CloudWatch RUM |
| Android macrobenchmarks | Synthetic CI perf tests | Device Farm |
| Embrace / bitdrift | Mobile observability vendors | n/a |
| Session replay | Reconstructed user session | CloudWatch RUM (partial) |

## Interview line

> On mobile I measure UX as completed intentions (checkout started vs finished), keep rich logs in a local ring buffer, and use server-pushed rules to upload sessions only for the cohorts and conditions I'm investigating. That's cheap, survives bad networks, and targets the tail.

## AWS mapping

- CloudWatch RUM + AppConfig feature flags for rule push (CloudWatch Evidently was discontinued in Oct 2025)
- Product analytics events joined with RUM by session ID (Amazon Pinpoint support ended Oct 2026)

## Practice question

**Q.** PM says checkout conversion dropped after release 3.2.8 but all your dashboards are green. Approach?

**Model answer.** Compute checkout completion by app version, OS, device tier, payment type, discount code and previous screen, comparing 3.2.8 with the prior version over the same rollout stage (to control for adoption bias). Look for the cohort with an outsized drop, then push a rule to capture session replays for abandoned checkouts in that cohort.

## Exercise

List three user intentions in your mobile app (for example, start checkout) and the outcome event that completes each. Each pair is an SLI.

## Takeaways

- Detect user impact first
- Local buffer + control plane = fidelity dial
- Segment, because P50 lies on devices

## Since the book (checked against documentation, 2026-11-27)

- CloudWatch Evidently was discontinued in October 2025 (AWS points to AppConfig feature flags) and Amazon Pinpoint support ended on 30 October 2026.
