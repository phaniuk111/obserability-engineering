# Lab 6: the pipeline (ch16, ch31)

**Goal:** treat the Collector as the place where policy is applied: what leaves your services is not what gets stored.

1. **PII.** The app puts the customer's email on the span (`user.email`). `make q F=06_pipeline`: no stored value contains an `@`, yet the number of distinct hashed emails equals the number of distinct users. The `attributes/pii` processor hashed it; same input, same hash, so you can still count and join.
2. **Read the pipeline** in `collector/local.yaml`. Three pipelines joined by connectors: everything goes to ClickHouse and to span metrics, then a `forward` connector feeds the sampling pipeline. Order matters: `memory_limiter` first, scrubbing before any exporter.
3. **Break the backend.** `docker compose stop clickhouse`, wait 30 seconds, `docker compose logs --tail 20 otel-collector`. The exporter retries and queues. `docker compose start clickhouse` and the backlog drains. Now look at `collector/production/gateway-collector.yaml`: there the queue is on disk (`sending_queue.storage`), so it also survives a Collector restart. [Resiliency docs](https://opentelemetry.io/docs/collector/resiliency/).
4. **Watch the Collector itself:** `curl -s localhost:8889/metrics | grep -c shop_` for what it emits; its own health is at http://localhost:13133.
5. `make lint` runs a structural check over all three configs: unused components, one-sided connectors, sampling in the wrong place.

**Check yourself**

- Why hash rather than drop the email? (Correlation without exposure. Security wants isolation, compliance wants evidence, observability wants correlation.)
- Where should Kubernetes enrichment run, and why not after tail sampling? (At the agent, next to the pod. Tail sampling regroups spans and loses the caller's identity.)
- What does an observability team own here? (This file, the shared attribute names, and the defaults in `app/telemetry.py`.)

**Try:** add an action that deletes `client.address`, restart the Collector, and confirm with lab 2's query 2a.
