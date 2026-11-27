# Lab 5: sampling (ch15)

**Goal:** see what tail sampling keeps, why naive numbers from sampled data are wrong, and how to correct them.

The Collector writes every span to `otel_traces` and the tail-sampled ones to `otel_traces_sampled` (and Jaeger). Policy, in `collector/local.yaml`: keep every trace with an error, every trace slower than 500 ms, 10% of the rest.

`make q F=05_sampling` (with the fault on for a while).

- **5a** how much was kept. In my run 12.4% of traces.
- **5b** naive vs weighted. Counting sampled traces gave 148; the truth was 1,192. The naive error rate was 6.1%, about eight times too high, because errors are kept at 100% and successes at 10%. Weighting each ordinary kept trace by 10 gave 1,246 and 0.72%.
- **5c** every error trace survived.

Three things to take away:

1. **Record the sample rate.** Here the weight can be derived from the policy. In general, store it on the event so the backend can multiply.
2. **Take metrics before sampling.** The Grafana dashboard is correct because `spanmetrics` sits in the pipeline before `tail_sampling`.
3. **Tail sampling needs the whole trace in one place.** With more than one Collector you need a routing tier in front (`collector/production/agent-collector.yaml`). [Tail sampling processor docs](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/tailsamplingprocessor).

**Check yourself**

- Head vs tail sampling: who decides, and when? (Head: at the first service, from the trace id, before anything is known. Tail: after the trace completes, using its content.)
- Why must a trace-level decision be consistent across services?
- What is the cost of tail sampling? (Memory for `decision_wait` × traces per second, and delay before data appears.)

**Try:** change `sampling_percentage` to 1, `docker compose restart otel-collector`, and fix the weight in 5b.
