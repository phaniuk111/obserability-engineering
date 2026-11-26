"""Pass 4 gap fill: items the gap check found in the raw notes but not in the
lessons, confirmed against the chapter text and merged by build.py."""

DEEPER = {
 "ch01": ["One checkout request in three silos: metrics give only fleet aggregates (48,291 requests, P99 380 ms, 0.3% errors), logs give five timestamped lines, and the trace shows where the 142 ms went (89 ms in the cart query). No silo links them to this user or build."],
 "ch02": ["Critical-path stakes range from 'a newspaper headline tomorrow' to '$20 million lost per minute of delay at market open' to 'someone could die'. Effort should match."],
 "ch03": ["In 2010 the typical stack was LAMP (Linux, Apache, MySQL, PHP), and monitoring plus dashboards worked. By 2026 there's no typical stack, and agents add nondeterminism."],
 "ch11": ["Known-unknowns you can alert on: disk 95% full, queue depth over 70%, a TLS certificate expiring in 10 days, error rate over 10% for five minutes.",
          "When challenged on cost, the open-weights model revised five nines down to 99.95% (about 42 minutes a year, under $1k lost on ~$12M/yr). Pushing back on the first answer is part of the method."],
 "ch12": ["Lookahead examples: a regression trending 99.9% → 99.88% over a month can wait for the next business day; trending to 98% within an hour pages someone now.",
          "Short-term linear example: 50 failures in the last day projects 400 more over 8 days, 450 in total, which beats the 438 budget, so exhaustion in about 8 days.",
          "Context-aware example: the budget was 65% remaining when the one-day baseline began and 35% now. Burning 30% a day exhausts it well within the 4-day lookahead, so alert.",
          "Read the burn pattern before acting: a gradual steady burn (e.g. 51.4% left), bursts (31.4% left), or one big drop (down to 1.3%) point to different kinds of failure."],
 "ch13": ["Complex aggregates need sketches: t-digest for percentiles like P99, HyperLogLog for COUNT DISTINCT.",
          "Other columnar engines used for observability: ClickHouse, Google BigQuery, Apache Druid. Observe Inc. built on Snowflake (great for warehousing, less interactive)."],
 "ch14": ["Example 14-4 result: /api/v1/orders served 40,723 requests with P95 1.034 s and P99 1.78 s, the obvious first target. Grouping by path × version × IP would be impossible as metrics.",
          "Two servers with 7.5 TB NVMe each (full copies for HA) hold about three days of data before object storage. Load-balancing writes across replicas reaches about 500k events/s.",
          "Replication uses the ReplicatedMergeTree engine; Map columns typically use CODEC(ZSTD(1))."],
 "ch18": ["The common complaint, 'the suite takes 5 minutes on my MacBook but 20 in CI', usually means CI starts from scratch every time. Persist the toolchain caches."],
 "ch19": ["Classic mobile debugging story: NullPointerExceptions across several screens. RUM sessions ending in the crash all show a tap on a button whose label has non-ASCII characters, and a string assumption in that button's code is the bug."],
 "ch20": ["Old utilisation rule: run Intel instances with SMT/hyperthreading at about 40% and Arm (no SMT) at 70–80%. Retest on current cores; Arm can run hotter because it isn't contending with itself.",
          "Purchasing models across clouds: reserved (Savings Plans, committed use), VMs (EC2, Azure VMs, GCE), interruptible (Spot, Azure Spot, Google Preemptible), elastic containers (Fargate, Azure Container Apps, Cloud Run), functions (Lambda, Azure Functions, Cloud Functions), or capex (e.g. Oxide racks).",
          "A minute of profile data is about 5 MB, but two hours isn't 120x that, because stacks repeat and compress well."],
 "ch21": ["Classic latency economics no longer transfer to AI: Greg Linden's 2006 Amazon result (+100 ms → revenue drop) and Google's (+0.5 s → −20% traffic) assumed speed was the main measure of UX."],
 "ch29": ["Matthew Sanabria (Oxide): use the vendor-neutral OTel Collector, not the vendor agent. Model costs for today and for growth, add a buffer for misconfigurations that spike the bill, and trust nothing that isn't in writing.",
          "If customers are genuinely fine with 98–99.5% availability, self-hosted open source can be much cheaper. Part of what a vendor sells is a stack independent of your own failures.",
          "Promotion incentives drive tech debt: engineers expect to reach principal faster by spending 18 months and $20M building an in-house platform than by picking a vendor and integrating it for a quarter of the cost."],
}

NAMES = {
 "ch03": [["Christine Yen","Honeycomb cofounder (analytics background)","n/a"],["LAMP","Linux, Apache, MySQL, PHP stack (2010 norm)","EC2 + RDS MySQL"]],
 "ch11": [["Google Customer Reliability Engineering (CRE)","Google programme teaching SLOs to customers","AWS Well-Architected reviews"]],
 "ch13": [["HyperLogLog","Approximate COUNT DISTINCT","Athena approx_distinct"],["Apache Druid / BigQuery","Other columnar engines","Amazon Redshift / Athena"]],
 "ch14": [["ReplicatedMergeTree","Replicated table engine via Keeper","n/a"]],
 "ch17": [["UCSD Design Lab: Agile Electrification","Open-source energy ontology playbooks","n/a"]],
 "ch20": [["SMT / hyperthreading","Two hardware threads per core; contend at high utilisation","Graviton has no SMT"]],
 "ch29": [["Matthew Sanabria (Oxide)","Practitioner advice on OTel + cost models","n/a"]],
}

NUMBERS = {
 "ch12": [["99.88% vs 98%","Ticket next business day vs page now"],["51.4% / 31.4% / 1.3%","Gradual, bursty, one-off burn examples"]],
 "ch14": [["1.034 s / 1.78 s","P95/P99 of the slowest endpoint in Example 14-4"],["7.5 TB × 2","NVMe pair ≈ 3 days before object storage"],["500k/s","Events/s with write load-balancing"]],
 "ch20": [["40% vs 70–80%","Old SMT vs Arm utilisation targets"],["5 MB/min","Profile size before compression"]],
 "ch29": [["98–99.5%","Availability where self-hosted OSS may be fine"],["18 months / $20M","In-house build promotion trap"]],
}

CHECKS = {
 "ch12": [dict(q="An SLO trending from 99.9% to 99.88% over the month should…", o=["Page immediately","Go to a ticket for the next business day","Be ignored","Trigger a rollback"], a=1, why="Slow burn; the 98%-in-an-hour case is the one that pages.")],
 "ch13": [dict(q="Which sketch computes COUNT DISTINCT at scale?", o=["t-digest","HyperLogLog","Bloom filter","Roaring bitmap"], a=1, why="t-digest is for quantiles.")],
 "ch20": [dict(q="Why can Arm instances often run at higher utilisation than SMT Intel?", o=["Faster clocks","No SMT threads contending with each other","Cheaper","More RAM"], a=1, why="Retest on current hardware anyway.")],
 "ch29": [dict(q="Sanabria's advice for avoiding lock-in and bill shock?", o=["Use the vendor agent","OTel Collector + written cost model with buffer","Self-host everything","Sign 5-year deals"], a=1, why="Trust nothing not in writing.")],
}

TERMS = {
 "ch13": [["HyperLogLog","Probabilistic sketch for COUNT DISTINCT"]],
 "ch20": [["SMT","Simultaneous multithreading: two hardware threads share a core"]],
}
