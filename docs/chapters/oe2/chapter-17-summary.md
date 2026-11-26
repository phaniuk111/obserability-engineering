# Chapter 17: Ontologies for humans and AI

Part 4: Technical deep dives. Coverage: Read in full from the book; text paraphrased.

## Summary

Frank Chen opens at 2 a.m.: the infrastructure dashboard is green and bills are wrong. Nothing is broken in code. The failure is in meaning. 'Availability' means server up, low latency, or a correct bill, depending on who you ask.

An ontology maps a domain's nouns, relationships and rules, and becomes real through semantic conventions. In the example: IntervalSeries (usage) + Tariff (rules) → BillSet (output); ActionPlan is the AI's untrusted proposal.

Invariants (coverage, arithmetic, determinism) become runtime assertions, a semantic firewall. In the AI sandwich, deterministic logic wraps the AI: simulate every proposal and reject any whose maths doesn't hold.

## Key ideas

- Provenance: every BillSet records input_series_id, applied_tariff_id and ruleset_version, so a cost spike can be traced to a data or logic change.
- CI gates: deterministic (hash, arithmetic, coverage), simulation (predicted savings reproduce within tolerance), semantic (golden dialogs, confidence floor around 0.6).
- Signal parity: CI emits the same JSON as production, so the assertion that blocks a PR is the query that pages.
- Signals: structural integrity, logic stability (ranking drift), AI reliability (proposal acceptance and eval pass rate).
- Rejected proposals become golden dialogs (PII scrubbed) and block deploys until passed. Eval pass rate is an SLI. In the example, a predicted $20 saving that simulates to $0.50 is logged as rejected/simulation_mismatch.

## You will learn

- Explain semantic failure vs infrastructure failure
- Define nouns, invariants and provenance for a domain
- Apply the AI sandwich and close the loop to evals

## Claims and numbers

| Figure | Context |
|---|---|
| ±$0.01 | Arithmetic tolerance |
| 0.6 | Example confidence floor |
| $20 vs $0.50 | Hallucinated vs simulated savings |

## Terms

| Term | Meaning |
|---|---|
| Ontology | Map of domain entities, relationships and rules |
| Invariant | Rule that must always hold |
| AI sandwich | Deterministic → AI → deterministic validation |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Palantir Foundry / Apache Jena / Apache Atlas / OpenMetadata | Ontology & metadata frameworks | AWS Glue Data Catalog, DataZone |
| Golden dialog | Ideal interaction used to score AI | Bedrock model evaluation |
| UCSD Design Lab: Agile Electrification | Open-source energy ontology playbooks | n/a |

## Interview line

> I never let an LLM act directly on financial data. It proposes a structured plan, a deterministic engine simulates it against invariants, and anything that fails is rejected and logged. The rejection rate is my AI reliability SLI, and rejections become evals.

## AWS mapping

- Step Functions: AI step between deterministic Lambda validators
- Bedrock Guardrails + evaluations; CloudWatch metrics on rejection rate

## Practice question

**Q.** An AI agent recommends tariff switches. How do you make it safe and observable?

**Model answer.** Define the ontology and invariants. Make the model emit a structured ActionPlan, simulate it against real usage, reject mismatches over tolerance, and log model, prompt version and rejection reason. Alert on rising rejection or falling acceptance. Turn rejected cases into eval fixtures.

## Exercise

Run pocs/08_ai_sandwich; add a 'max shift per hour' invariant and a test.

## Takeaways

- Semantic failures hide behind green dashboards
- Invariants constrain outputs you can't enumerate
- Production failures feed the eval suite
