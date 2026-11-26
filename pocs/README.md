# POCs: Observability Engineering, 2nd Edition

Ten small programs, one per big idea in the book. Python 3.10+ and the standard library only, so you can read every line. Each folder has a module and a `test_*.py`. The tests double as worked examples you can talk through in an interview.

```bash
./run_all_tests.sh        # 73 tests, under a second
python3 01_wide_events/wide_events.py   # some modules also print a demo
```

| # | Folder | Book idea (chapter) | What it proves | Nearest AWS service |
|---|---|---|---|---|
| 01 | `01_wide_events` | Wide structured events; derive metrics/logs/traces at read time; average-of-averages trap (ch1, ch5, ch6) | Overall P99 hides a slow cohort; slicing by build × flag × region finds it with no schema change. 183 ms (naive) vs 175 ms (correct). | CloudWatch Logs Insights or Athena over JSON wide events; X-Ray annotations |
| 02 | `02_mini_tracer` | Tracing = fancy logs + passing IDs; W3C `traceparent`; span links; critical path (ch5, ch7, ch18, ch22) | Context propagates in-process (contextvars) and across services (headers); async hops use links; the critical path ignores parallel work that finishes early. | AWS X-Ray / ADOT; Application Signals |
| 03 | `03_bubbleup` | Automating the core analysis loop (ch8) | Recreates the us-east-1a incident: the AZ value is in ~100% of slow events vs ~17% of baseline. Iterating finds a three-factor cause. | CloudWatch Contributor Insights (partial); Honeycomb BubbleUp is the reference |
| 04 | `04_slo_burn` | Error budgets; event vs time SLIs; relative and predictive burn alerts; port of the book's Go `isBurnViolation` (ch11, ch12) | Book arithmetic reproduced: 99.9% ≈ 8h45m/yr; 10M req, 15-min windows → 4x ≈ 13, 20x ≈ 69 failures; proportional projection 720 > 438. | CloudWatch Application Signals SLOs; burn-rate alarms |
| 05 | `05_sampling` | Sample rate on every event; weighted percentiles; consistent sampling; per-key target rate; tail sampling (ch4, ch15) | Weighted median of {1×5, 3×2, 7×9} is 7, not 3. Consistent sampling never orphans a child span. Errors keep far higher rates than 200s. | ADOT Collector `tail_sampling`; X-Ray sampling rules |
| 06 | `06_columnar_store` | Retriever-style storage: time segments, column files, dictionary encoding, pruning, top-K, hedged reads; TSDB cardinality explosion (ch13, ch14) | Only overlapping segments and referenced columns are read. A stuck segment read is rescued by re-issuing the slowest 10%. Adding `user_id` turns 4 series into thousands. | S3 + Athena/Parquet; ClickHouse on EC2/ClickHouse Cloud; Lambda fan-out |
| 07 | `07_telemetry_pipeline` | Collect → normalize → secure → enrich → reduce → route; buffering, backoff with jitter, backpressure; tiered service (ch16, ch27, ch7) | Free-text PII redacted, IDs stably hashed, health checks dropped, duplicates collapsed, security events fanned out to a SIEM. Data stays queued when the backend is down. | ADOT/OTel Collector on EKS (agent + gateway); Kinesis Firehose; Security Lake |
| 08 | `08_ai_sandwich` | Ontology + invariants; AI proposals validated by a deterministic core; LLM cost at query time; harness repair; promote traces to evals (ch17, ch21) | A plan claiming $20 savings that simulates to $3 is rejected with `simulation_mismatch`. Proposal-rejection rate is the AI reliability SLI. | Bedrock + CloudWatch GenAI observability; Step Functions for the sandwich |
| 09 | `09_cost_and_ci` | Bin-packing, cloud bill as wide events, CI retries vs tail latency, Amdahl, build-vs-buy cost (ch18, ch20, ch29) | 20-vCPU pods on 32-core nodes strand 11 cores. Retries cut failures but double P99 while P50 stays flat. A "free" ELK stack runs to about $2M a year. | Cost and Usage Report → Athena; Karpenter; CodeBuild/GitHub Actions + OTel |
| 10 | `10_mobile_ring_buffer` | Local ring buffer + server-pushed FSM rules; user-focused SLI (ch19) | Sessions upload only when a rule fires, such as abandoning checkout. A new discount-code format shows up as a 40-point completion-rate gap. | CloudWatch RUM; Amplify/Pinpoint events; AppConfig for rule push |

## Infrastructure examples

- `otel/gateway-collector.yaml`: a gateway Collector with PII hashing and redaction, k8s enrichment, tail sampling (errors + slow + 10%), span-derived RED histograms, fan-out to a vendor, S3 archive and Amazon Managed Prometheus, and a persistent queue. The YAML parses. The processor names follow the OTel contrib distribution. Check them against your Collector version.
- `terraform/telemetry_archive/main.tf`: an encrypted, private S3 bucket with lifecycle tiering (IA at 90 days, delete at 365, errors kept 730), plus an alarm on Collector export failures. Terraform wasn't available here, so run `terraform validate` before you use it.

## Interview angle

Each test name is a claim you can defend: "the critical path ignores parallel shorter work", "head sampling misses rare errors", "one bad minute burns a quarter of a four-nines budget". Read a test, then explain why it's true without the code.
