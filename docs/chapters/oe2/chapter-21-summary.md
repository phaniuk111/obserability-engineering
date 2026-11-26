# Chapter 21: Observability for LLM applications

Part 5: Use cases. Coverage: Read in full from the book; text paraphrased.

## Summary

LLMs are opaque (no debugger), nondeterministic (temperature doesn't guarantee repeatability), fed an unbounded input space, and changing fast. Fast but wrong answers don't satisfy users, and in agents one failed tool call matters less than whether the task got done.

Evals are like tests with three outcomes: pass, fail, maybe. Honeycomb's Canvas uses question evals (string-match facts from golden data) and task evals (score the investigation steps). Great evals can still sit alongside bad UX.

The flywheel: production traces become eval cases, evals guide harness and prompt fixes, and the fixes show up in telemetry.

## Key ideas

- Follow the OTel GenAI semantic conventions: tokens in/out, model, sampling parameters, prompts on client spans.
- Decide how much input/output to store. Link to a system of record rather than inlining large bodies. Mind privacy.
- Derive cost at query time from model + tokens; there's no standard cost attribute. Record feedback (thumbs, retries) as attributes.
- Put prompt-cache hit info on spans. Track provider rate limits, retries and latency, and use SLOs rather than thresholds for provider failures.
- Honeycomb's MCP server SLO was 90% query success. They found calling models guessed field names and mishandled time ranges.
- Query Assistant: 25% errors, down to ~14% with harness repairs (e.g. drop the column on COUNT), down to under 1% with prompt work. Then they shipped COUNT-with-column because users clearly wanted it.
- is_slow (a calculated field, >500 ms) was misread as a cause until it got a description. Public benchmarks can mislead about your users.
- Classic latency economics no longer transfer to AI: Greg Linden's 2006 Amazon result (+100 ms → revenue drop) and Google's (+0.5 s → −20% traffic) assumed speed was the main measure of UX.

## You will learn

- Explain why latency isn't UX for LLM apps
- Design LLM telemetry with OTel GenAI conventions
- Run the eval ↔ telemetry flywheel

## Claims and numbers

| Figure | Context |
|---|---|
| 25% → 14% → <1% | Query Assistant error rate |
| 90% | MCP server success SLO |
| 100 ms ≈ 1% sales | Amazon latency finding |
| 0.5 s → −20% traffic | Google 2006 finding |

## Terms

| Term | Meaning |
|---|---|
| Eval | Expected-output test for nondeterministic systems |
| Harness | Deterministic code around the model |
| Golden data | Hand-crafted representative inputs with known answers |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| OTel GenAI semantic conventions | Standard LLM span attributes | Bedrock + ADOT |
| LLM-as-a-judge | Model grades outputs | Bedrock model evaluation |
| Apdex | Latency-based satisfaction index | CloudWatch Apdex in RUM/AppSignals |

## Interview line

> For LLM features I instrument the full harness, not just the model call: tokens, model, prompt version, tool calls, validation repairs and user feedback. I promote bad traces to evals. Cost is derived from tokens at query time so I can compare prompt versions.

## AWS mapping

- Bedrock invocation logging + CloudWatch GenAI observability
- Bedrock evaluations; SLOs on model invocation success/latency

## Practice question

**Q.** Your LLM feature errors 25% of the time. Plan?

**Model answer.** Group errors by type from traces. Validation failures that are nearly right get deterministic repair in the harness. Then improve prompts and tool descriptions against an eval set built from real failing traces. Watch for errors that reveal unmet user needs, and change the product. Set an SLO on success excluding provider timeouts.

## Exercise

Run pocs/08_ai_sandwich LLM tests; add a feedback-weighted eval promotion rule.

## Takeaways

- Telemetry fuels evals; evals fuel fixes
- Code fixes beat prompt tweaks surprisingly often
- Describe fields; models impute meaning
