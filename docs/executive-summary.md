# Executive summary

*Observability Engineering, 2nd Edition (Majors, Fong-Jones, Miranda, with Parker; O'Reilly 2026)* argues that observability is a property of dependable software: how well you can explain any system state, including ones you've never seen, from the telemetry you already have. Its central technical claim is that wide, structured, high-cardinality events, stored once in a columnar store and aggregated at read time, beat the three pillars (separate metrics, logs and traces) for code you write. The three pillars stay right for infrastructure (ch1, ch3, ch25).

## Main arguments

1. **Unify the data.** Metrics, logs and traces are all structured events. Capture one wide event per unit of work and derive the rest when you need it (ch5, ch6). Pre-aggregation is a one-way trip (ch1).
2. **Instrument deliberately with OpenTelemetry.** Combine auto and custom instrumentation, create spans only for interesting and aggregable work, layer signals, and keep naming consistent with schemas (ch4, ch7).
3. **Analyse from first principles.** The core analysis loop, automated as baseline-vs-anomaly diffing, lets any engineer debug unfamiliar systems (ch8). Observability is the telescope that aims the debugger (ch9).
4. **Alert on user pain.** Event-based SLIs and predictive burn alerts replace threshold alert fatigue (ch11, ch12).
5. **The data platform is solvable.** Time-partitioned columnar storage (Retriever, ClickHouse), sampling with recorded rates, and telemetry pipelines make it affordable (ch13–ch16).
6. **Context is everything for AI.** Agents need an explicit context layer. AI outputs need deterministic invariants. LLM features need evals fed by telemetry (ch10, ch17, ch21).
7. **Learning speed is the constraint.** With AI, generating code is cheap and validating it is not. Observability is the sensing part of every delivery feedback loop. Run it as a platform product and an investment, not a cost center (ch23–ch29).

## Where the parts meet

The same idea repeats at every level. A precise, context-rich signal closes a feedback loop: a deploy (ch2), a canary (ch2), an SLO burn (ch12), a CI build (ch18), a mobile cohort (ch19), an LLM eval (ch21), Fin's latency and cost (ch22), and the organisation's own learning (ch24, ch25).

## Turning this into interview answers

Lead with an outcome, name the mechanism, give one number. Example: "Event-based SLIs: a minute where 6% of requests are slow burns 6% of budget, not 100%, which matters at four nines where the month's budget is about 4.4 minutes." The course page has an interview line per chapter and a drill bank.

## Not covered

Chapters 30–32 (vendor partnerships, instrumentation for observability teams, where we go from here) were not read: the browser session disconnected. Some figures in Part IV/V were checked from captions only, without viewing the image (noted in docs/progress.md).
