# Lab: a real observability stack you can run

Three small services instrumented with the OpenTelemetry SDK, an OpenTelemetry Collector, ClickHouse as the event store, Prometheus for SLO alerts, Jaeger and Grafana to look at it. A fault you switch on, and seven labs that find and measure it the way the book describes.

```
storefront ─► cart
     │──────► payments          apps export OTLP
     ▼
OTel Collector ── scrub PII ──┬─► span metrics (100% of spans) ─► Prometheus ─► burn-rate alerts, Grafana
                              ├─► ClickHouse otel_traces (every span: the wide-event store)
                              └─► tail sampling ─► ClickHouse otel_traces_sampled, Jaeger
```

## Run it

```bash
make up          # needs Docker; builds the app, starts 9 containers, prints the URLs
make smoke       # optional: starts the stack and checks 11 things the labs rely on
make fault-on    # break discount validation for new-format codes
make q F=03_bubbleup
make down
```

No Docker? `make test` runs the same services with the real SDK, captures their OTLP export, loads it into an embedded ClickHouse engine and runs every lab query (`pip install -r app/requirements.txt chdb pyyaml`). `make nodocker` prints the query results.

## Labs

| # | Lab | Book | You will be able to say in an interview |
|---|---|---|---|
| 1 | [Follow one request](labs/01-traces.md) | ch6, ch7 | How context propagates, what a span link is for, when to use baggage |
| 2 | [Wide events and high cardinality](labs/02-wide-events.md) | ch1, ch5 | Why raw events beat pre-aggregated metrics for debugging |
| 3 | [Find the culprit without a hypothesis](labs/03-core-analysis-loop.md) | ch8 | How you debug a system you have never seen |
| 4 | [SLOs and burn alerts](labs/04-slo.md) | ch11, ch12 | Event-based SLIs, burn rate, multi-window alerts |
| 5 | [Sampling](labs/05-sampling.md) | ch15 | Tail vs head sampling, and how to get true counts back |
| 6 | [The pipeline](labs/06-pipeline.md) | ch16, ch31 | PII handling, backpressure, why metrics are taken before sampling |
| 7 | [Storage](labs/07-storage.md) | ch13, ch14 | Why columnar storage makes this affordable |
| 8 | [From lab to production](labs/08-production.md) | ch16, ch29–31 | Two-tier Collectors, durability, AWS mapping |

## What was verified, and how

| Part | Status |
|---|---|
| App instrumentation (traces, links, baggage, metrics, stable HTTP attribute names) | Run and tested here with the real SDK and OTLP (`make test`, 19 tests) |
| All SQL in `clickhouse/queries/` | Run here on the ClickHouse engine (chdb 4.5, engine 26.11) against data the app produced |
| Collector configs | Structural lint here; checked against the component docs. Not run through a Collector |
| `docker-compose.yaml`, Prometheus rules, Grafana provisioning | Parsed here; not started (no Docker daemon where this was built). `./smoke-test.sh` is the check |
| `aws/terraform` | Parsed with an HCL parser; not `terraform validate`d or applied |

In `make test`, two Collector behaviours are imitated in Python because no Collector could run there: hashing `user.email` and the tail-sampling policy. `tests/harness.py` says where.

If the smoke test fails on metric names, see the hint it prints: span-metric naming is the part most likely to differ between Collector releases.
