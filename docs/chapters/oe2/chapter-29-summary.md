# Chapter 29: Build vs buy vs open source

Part 6: Governance. Coverage: Read in full from the book; text paraphrased.

## Summary

Decide which you hate more, your money or your time. Name your biases: engineers want to build (surgeons want to cut), plus sunk cost, not-invented-here, and fear of migration.

Rick Clark's 2×2: business value × ubiquity. Build bespoke differentiators (e.g. Retriever for Honeycomb). Buy commodity, low-value things. Bespoke, low-value things should not exist. Commodity things with high value need a real decision. Peter Corless' version for open source: create, adopt, acquire, avoid, plus commission.

Default for most: buy the platform, build the integration layer. Observability is unusual software: it watches the watchers, so it must not go down with your production stack.

## Key ideas

- Should-not-exist example: a bank's custom Apache 1.3 request handler outlived its authors and cost over $10M to unwind once it became a compliance issue.
- 'Free' ELK: vs an ~$80k/month quote, it actually cost $80k/month in hardware plus three engineers and recruiting, over $2M a year.
- Decide-quadrant questions: the job to be done, how unique you really are, the smallest version, product management, timeline, who supports it. Near the disk: battle-tested. Near the UX: custom is fine.
- Examples: SLO tooling, buy ~90%. A ~200-line React OTel wrapper, build it (two weeks). Chargeback, use vendor tags plus a script.
- Open source is free as in puppies, not beer. Pricing red flags: per-seat, per-host, per-service, per-query models that penalise curiosity. A Gartner customer growing 48% a year for 15 years implies about 358x the cost.
- Avoid lock-in: native OTel plus distros, the Collector not vendor agents, written cost models with buffers. The observability team writes libraries, standardises naming, manages vendors and educates.
- Caveats: no big vendor sells monitoring at monitoring prices; hyperscalers may build; enterprises need tiers.
- Matthew Sanabria (Oxide): use the vendor-neutral OTel Collector, not the vendor agent. Model costs for today and for growth, add a buffer for misconfigurations that spike the bill, and trust nothing that isn't in writing.
- If customers are genuinely fine with 98–99.5% availability, self-hosted open source can be much cheaper. Part of what a vendor sells is a stack independent of your own failures.
- Promotion incentives drive tech debt: engineers expect to reach principal faster by spending 18 months and $20M building an in-house platform than by picking a vendor and integrating it for a quarter of the cost.

## You will learn

- Apply the build/buy 2×2 and its OSS-aware version
- Calculate the hidden cost of 'free'
- Spot pricing and lock-in traps; run a buy-and-build platform

## Claims and numbers

| Figure | Context |
|---|---|
| >$10M | Cost to unwind the custom Apache module |
| ~$80k/month | Vendor quote in ELK example |
| >$2M/yr | Real cost of 'free' ELK |
| 358x | Cost growth at 48%/yr for 15 years |
| ~200 LOC / 2 weeks | Build-worthy OTel wrapper |
| 98–99.5% | Availability where self-hosted OSS may be fine |
| 18 months / $20M | In-house build promotion trap |

## Terms

| Term | Meaning |
|---|---|
| Decide quadrant | High value commodity: debate build vs buy |
| Commission | Pay others to build code you then own |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Rick Clark 2×2 | Build/buy/should-not-exist/decide | n/a |
| Peter Corless framework | Create/adopt/acquire/avoid/commission | n/a |
| Heidi Waterhouse | 'Free as in puppies' | n/a |
| OTel distro | Vendor-configured OTel bundle | ADOT |
| COTS | Commercial off-the-shelf | AWS Marketplace |
| Matthew Sanabria (Oxide) | Practitioner advice on OTel + cost models | n/a |

## Interview line

> Observability backends are commodity for almost everyone, so I buy the platform, use OTel so I can leave, and build the thin layers that are ours: instrumentation wrappers, naming standards, cost attribution.

## AWS mapping

- ADOT as vendor-neutral distro; Marketplace private offers; managed Grafana/Prometheus for ops loop

## Practice question

**Q.** Engineers propose building our own observability stack on OSS to save money. Evaluate.

**Model answer.** Price it fully: hardware, three or more engineers, recruiting, upgrades, on-call, opportunity cost, and HA independent of our own production (it has to stay up when prod is down). Compare with a vendor quote modelled for 1–2 years of query growth. Unless we're hyperscale or observability is our product, buy and build integrations on OTel.

## Exercise

Place five components of your stack on the 2×2. Price one 'free' open-source option in full: hardware, three engineers, on-call, upgrades.

## Takeaways

- Buy the platform, build the glue
- Price the whole puppy
- Pricing must not punish curiosity

## Hands-on

[Lab 8: From lab to production](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/08-production.md)

## Official documentation

- [AWS services in maintenance](https://docs.aws.amazon.com/general/latest/gr/maintenance_services.html): Check before you depend on a managed service
