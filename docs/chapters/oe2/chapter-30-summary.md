# Chapter 30: Vendor engineering: running the evaluation and the migration

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

Buying observability is engineering work, not shopping. The book calls it vendor engineering: getting an outcome across team and company lines where you have influence but no authority. Most tool transformations fail, and the ones that work run on trust and credibility as much as on technical merit.

Inside your company, assume shared goals and earn two things. Credibility: what you claim turns out to be true, so claim conservatively. Trust: people believe you act in their interest, so help with their goals first. With vendors, assume different goals: they help while you move toward a sale. Aim for a deal both sides are glad they signed.

The path: agree scope, an executive sponsor and measurable success criteria before anything else. Adopt OpenTelemetry so this is the last re-instrumentation. Run a POC that load-tests your worst real problems. Build champions, keep procurement moving, migrate in three steps, and do not call it done until the old tool is switched off.

## Key ideas

- Stakeholders and what they need. Engineering: show the tool fixing their pain (follow the pain, find champions). Management: fit with direction and opportunity cost, with written progress updates. Finance: cost, predictability, ROI, time to value; rough directional numbers are acceptable. IT/ops and security: data handling, access, compliance evidence. Procurement: treat them as an ally, never route around them.
- Never accept a proxy no. When someone says another team will block it, go and ask that team directly. Compliance is usually more flexible than rumoured when you bring the right evidence.
- You will not be in the room when the decision is made, so write the case for your sponsor in business outcomes and polish it. A surprise can sink the deal, so share bad news and large numbers early.
- Vendor trust check: are they honest when the answer is unflattering? Do they spread fear about competitors or plant trap questions? Do they help design a POC that exercises hard cases, or offer to run it for you on a tidy dataset? Double-check anything they say about a competitor.
- Ways to influence a vendor's roadmap: being an important customer, strategic alignment, sweat equity, technical credibility and personal relationships, and formal levers (SLAs, OKRs, KPIs). Back channels are fragile, so write things down.
- SLAs encode the vendor relationship the way SLOs encode the one between engineering and the business. Don't leave them to procurement at the end; they outlast the people who negotiated.
- POC contents: a description of your pain (the events that triggered this), a definition of success, required capabilities written as questions and workflows rather than solutions, and scope (teams, datasets, what is out). Time-box it, resource it, and agree up front to proceed if it passes.
- POC rules: real production load, not a demo dataset. Instrument so each vendor is seen at its best rather than forcing an identical lowest-common-denominator setup. Don't let a vendor write your requirements, and watch for poison-pill capabilities a rival planted. Separate users from gatekeepers.
- Pricing: list prices mean little. Send a representative slice (one cluster) and extrapolate. Ask a comparable reference customer what they pay and how many engineer-cycles go on managing cost.
- Dual-write during evaluation and migration with two OTel exporters, so old and new run side by side on the same data.
- Migration in three steps: de-risk with one non-trivial service, bulk-migrate and accept some mess, then iterate service by service. Don't import the old tool's dashboards and alerts wholesale; rebuild from what the business needs. Put milestones in OKRs.
- The last 10% is the hardest. Publish a deprecation timeline, switch the old tool off, and celebrate. Then write a retro and requalify vendors on a regular cadence; a parallel test often produces a discount.
- Colleagues may see you as a threat to their tools (identity) or turf, and some will escalate or tip off the incumbent vendor. Keep asking for dissent early, and keep offering a hand.
- Origin story: at a 2013 meeting between Parse, Facebook and MongoDB, Mark Callaghan's quiet questions led to a pluggable storage engine API, MongoRocks (up to 90% less disk) and an introduction to WiredTiger, now MongoDB's default engine.

## You will learn

- Map the stakeholders in a tooling purchase and what each one needs
- Design a vendor POC that tests your hardest problems
- Plan a migration through to decommissioning the old tool

## Claims and numbers

| Figure | Context |
|---|---|
| up to 90% | Disk reduction from MongoRocks in the origin story |
| 3 steps | De-risk, bulk migrate, iterate |
| last 10% | The hardest part of a migration |
| $40M/yr, 17 years | Fictional 'Fort Pillars' incumbent vendor |
| 14 h across 5 tools | Fictional 'Tool Sprawl' P0 incident |
| 40–50% in 90 days | Cost cut expected in the consolidation scenario |

## Terms

| Term | Meaning |
|---|---|
| Proxy no | A refusal relayed on someone else's behalf |
| Sweat equity | Effort you invest that earns influence with a vendor |
| Poison pill capability | A requirement seeded to disqualify competitors |
| Champion | An engineer who gains from the change and says so |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Vendor engineering | Technical leadership across company lines to buy and adopt tools | n/a (practice) |
| Mark Callaghan | Facebook database engineer in the origin story | n/a |
| MongoRocks / WiredTiger | Storage engines that came out of the pluggable-engine push | n/a |
| Dual write | Send the same telemetry to old and new backends | Two exporters in an ADOT/OTel Collector pipeline |
| SLA | Contract on service quality with remedies | AWS Marketplace private offer terms |
| Requalification | Re-testing vendors on a schedule | n/a |

## Interview line

> I'd run it as an engineering project: sponsor and written success criteria first, a POC on our hardest production problems with dual-written OTel data, a rubric to compare vendors, and a migration plan that ends with the old tool switched off.

## AWS mapping

- Dual-write from one Collector: `otlp_http` exporter to the candidate plus the existing CloudWatch/X-Ray path, so both see identical data
- AWS Marketplace private offers for the commercial side; CUR tags to track the old and new tool's cost during overlap

## Practice question

**Q.** You're asked to lead the replacement of a long-standing monitoring vendor. How do you run the evaluation?

**Model answer.** Start with who can sign and who owns budget, and get scope and measurable success criteria agreed in writing with someone near that budget. Map stakeholders and talk to security and procurement directly rather than accepting second-hand objections. Move instrumentation to OpenTelemetry so data can be dual-written. Write the POC around our real pain: the incidents that took longest, the questions we couldn't answer. Run it on production load for a fixed period, score vendors with a rubric, and validate price on a representative slice. Line up champions from the teams in the most pain. After signing: migrate one hard service, then bulk, then iterate, with OKR milestones and a published date for decommissioning the old tool.

## Exercise

Write a one-page POC brief for a tool you use: pain, definition of success, three required capabilities phrased as questions, scope, time box.

## Takeaways

- Sponsor, scope and success criteria first
- POC = your hardest problems on real load
- Not done until the old tool is off

## Hands-on

[Lab 8: From lab to production](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/08-production.md)
