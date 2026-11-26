# Chapter 28: The organizational shift

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

Rick Clark (UST) argues many orgs have legacy observability wearing a new label. War rooms, manual correlation, the same three people, folklore mysteries.

Five tests. Ownership: how do you know your merge works? Two-or-three people: 60–80% of engineers should investigate alone. Mystery: what weirdness do we just accept? Arbitrary question: answer a never-asked slice in under 60 seconds. Deployment confidence: read-only Fridays and CABs are fear signals.

Change needs a coalition (people who feel the pain, plus the heroes who held things together), a mandate with real authority, and a product-minded roadmap.

## Key ideas

- Resistance: the organisational immune response (committees, starved pilots, redefined success) — name it aloud. Vendors are incentivised to sell tiers, AI add-ons and services. Teams are protecting identity ('I'm the Splunk person') and headcount. Leadership carries sunk cost and memories of failed consolidations.
- Rick's mistake: bypassing the principal network architect, who controlled IP allocation. Requests that should take hours took weeks until he was brought in.
- Pitch it as risk reduction, capability and burden (best engineers spending 30% of their time in war rooms). Not consolidation, not cost savings. Mention open standards and the AI forcing function.
- Roadmap: one domain at full depth; paved paths; platform engineering principles (build little, use OTel); rerun the tests at 6 months; expand gradually (budget shifting about 10% in year one to 40% by year three).
- Team: platform, SDKs, standards, vendors, DX, not instrumenting every service. Use Wardley's pioneers, settlers and town planners. Turn 'Splunk person' into 'telemetry architect'. Don't promise no jobs change.

## You will learn

- Run the five tests for legacy-masquerading-as-modern
- Handle resistance from vendors, teams and leadership
- Secure a mandate and run the roadmap and team

## Claims and numbers

| Figure | Context |
|---|---|
| 60–80% | Engineers who can investigate independently (modern) |
| <60 s | Arbitrary question answer time |
| 30% | War-room share of top engineers' time |
| 10% → 40% | Budget shift year 1 → year 3 |

## Terms

| Term | Meaning |
|---|---|
| Organisational immune response | Reflexive defence of the status quo |
| Mandate | Authority making the new way required |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Simon Wardley: pioneers/settlers/town planners | Match people to phases | n/a |
| Strangler pattern | Incremental replacement (budget too) | n/a |
| Vendor-silo alignment | Identity tied to one tool | n/a |

## Interview line

> I'd prove the gap with five evidence tests, build a coalition including the legacy experts, get a mandate that new services instrument the new way, and start with one domain instrumented deeply. Success is war rooms stopping and Friday deploys being boring.

## AWS mapping

- Mandate implementation: EKS admission policy or service template requiring OTel resource attributes

## Practice question

**Q.** The 'Splunk team' resists your OTel plan. What do you do?

**Model answer.** Bring them in early. They hold real knowledge and often real control over resources. Be honest that roles will change, and show the path: OTel skills travel with them, and pioneers, settlers and town planners each have work. Build the case with them using the five tests so the evidence is shared.

## Exercise

Run the five tests with three engineers this week; record answers verbatim.

## Takeaways

- Evidence over opinion
- Honour the heroes
- Authority, not just sponsorship
