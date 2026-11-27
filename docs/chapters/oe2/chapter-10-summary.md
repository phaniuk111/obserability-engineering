# Chapter 10: AI agents for observability

Part 3: Analysis workflows. Coverage: Read in full from the book; text paraphrased.

## Summary

Boris Tane argues it all comes down to context. An agent with telemetry access can run a multistep investigation. In the book's example: alert, error-rate query, slow traces, correlated logs, then the codebase, ending with a 2 s retry timeout against a 5 s upstream SLA.

Without context, agents struggle. They don't know what they don't know. Naming is chaotic (user-service vs users-svc vs legacy-user-api). The data surface is huge. They confuse correlation with causation.

Proven uses: the first 15 minutes of incident groundwork, explaining traces (that waterfall is an N+1 from an ORM), raising instrumentation quality as code is written, auditing alerts, and proposing data-grounded SLOs.

## Key ideas

- Six context layers: service topology, naming conventions and aliases, deployment context, known issues, recent incidents (last 30 days), business context (revenue-critical endpoints, thresholds).
- The mental model is disappearing. Coding agents ship code humans never study, so institutional knowledge forms more slowly. Make it explicit and keep it current.
- Augment the on-call engineer; don't automate resolution end to end yet.

## You will learn

- Explain why natural-language querying alone fails
- Name proven agent use cases
- Design the context layer agents need

## Claims and numbers

| Figure | Context |
|---|---|
| 15 min | Mechanical incident groundwork agents can take |
| 2 s vs 5 s | Retry timeout vs upstream SLA in the example |

## Terms

| Term | Meaning |
|---|---|
| Context layer | Machine-readable topology, names, deploys, incidents, business context |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| N+1 query | Sequential per-row DB calls from ORM misuse | RDS Performance Insights |
| Context engineering | Curating what an agent sees | Bedrock knowledge bases |

## Interview line

> An observability agent is only as good as its context. Before building one I'd publish a machine-readable map of topology, names, owners, recent changes, incidents and business criticality. Then let it do the first 15 minutes of triage while a human decides.

## AWS mapping

- Bedrock AgentCore agent + tools over CloudWatch/X-Ray APIs + a service catalog as context
- CloudWatch investigations (GA June 2025; previewed as Amazon Q Developer operational investigations)

## Practice question

**Q.** Leadership wants an AI SRE to auto-resolve incidents. What's your plan?

**Model answer.** Start with copilot-style triage: gather recent deploys, error and latency deltas, top correlated dimensions and exemplar traces, and post a summary with hypotheses. Build the context layer first. Measure whether it shortens time to understanding, then widen autonomy only on reversible actions with guardrails.

## Exercise

Write a YAML 'context card' for one service: aliases, owner, dependencies, known issues, revenue criticality.

## Takeaways

- Context beats model
- Augment humans in incidents
- Explicit knowledge replaces vanishing tacit knowledge

## Since the book (checked against documentation, 2026-11-27)

- The AWS feature previewed as 'Amazon Q Developer operational investigations' became generally available in June 2025 under the name CloudWatch investigations.

## Official documentation

- [Amazon CloudWatch investigations (GA announcement)](https://aws.amazon.com/about-aws/whats-new/2025/06/ga-accelerate-troubleshooting-amazon-cloudwatch-investigations): AWS's AI-assisted investigation feature
