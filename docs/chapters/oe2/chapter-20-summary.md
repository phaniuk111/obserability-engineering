# Chapter 20: Performance engineering

Part 5: Use cases. Coverage: Read in full from the book; text paraphrased.

## Summary

Honeycomb found load-balancer latency that its traces didn't show. A pprof flame graph showed regexp.Compile using 17% of CPU, because the HTTP router was rebuilt on every request. The fix was five lines, and tracing couldn't have seen it.

Tracing is the forest; profiling shows the tree rings. Account for request time to about 100 ms with spans, then use sampling profilers (about every 10 ms) for function-level detail. Read flame graphs by width (total time) and stacking (call chains). Continuous profiling is cheap because profiles repeat and compress.

Cost: choose compute models (capex, reserved, VMs, spot, Fargate/Cloud Run, Lambda) from load data. Squeeze fleets until the SLO tail degrades. Test new hardware generations and Arm (about 30% better price-performance per generation).

## Key ideas

- Kubernetes: use heatmaps rather than percentiles for node saturation. Ingest Karpenter/Cluster Autoscaler logs. Watch rollout surges double apparent pod counts (group by template hash), and DaemonSet overhead. Bin-packing: 20-core pods on 32-core nodes strand 11 cores, so use 64-core nodes or 15-core pods.
- Serverless: cold-start init is billed, so instrument init, running and sleeping spans. Lambda Power Tuner. S3 reads are about 25% of Retriever's serverless cost. Provisioned concurrency is the worst of both worlds.
- Ingest the cost and usage report as wide events. Watch NAT gateway and cross-AZ transfer. Size savings plans from your minimum hourly spend.
- Per-customer profiling found protobuf→JSON serialisation repeated per Lambda invocation (fixed by caching) and deeply nested if/else queries (fixed by adding switch).
- Brendan Gregg's books are the reference.
- Old utilisation rule: run Intel instances with SMT/hyperthreading at about 40% and Arm (no SMT) at 70–80%. Retest on current cores; Arm can run hotter because it isn't contending with itself.
- Purchasing models across clouds: reserved (Savings Plans, committed use), VMs (EC2, Azure VMs, GCE), interruptible (Spot, Azure Spot, Google Preemptible), elastic containers (Fargate, Azure Container Apps, Cloud Run), functions (Lambda, Azure Functions, Cloud Functions), or capex (e.g. Oxide racks).
- A minute of profile data is about 5 MB, but two hours isn't 120x that, because stacks repeat and compress well.

## You will learn

- Combine tracing and profiling
- Pick compute purchasing models and squeeze fleets with data
- Find Kubernetes and serverless cost waste

## Claims and numbers

| Figure | Context |
|---|---|
| 17% | CPU in regexp.Compile |
| 5 lines | Size of the fix |
| ~30% | Arm price-performance gain per generation |
| 11 cores | Stranded per 32-core node |
| 25% | S3 reads share of Retriever serverless cost |
| 100 ms | Account for time to this granularity with spans |
| 40% vs 70–80% | Old SMT vs Arm utilisation targets |
| 5 MB/min | Profile size before compression |

## Terms

| Term | Meaning |
|---|---|
| Flame graph | Stacked call-stack visualisation; width = time |
| Continuous profiling | Always-on low-overhead profile collection |
| Bin-packing | Fitting workloads onto nodes to avoid stranding |
| SMT | Simultaneous multithreading: two hardware threads share a core |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| pprof / flame graph | Go profiler / visualisation | CodeGuru Profiler |
| Java Flight Recorder | JVM profiler | CodeGuru Profiler |
| Pyroscope / Polar Signals / zymtrace | Continuous profiling | Grafana Pyroscope on AMG |
| Karpenter + Node Termination Handler | Spot-friendly autoscaling | EKS |
| Graviton / Cobalt / Axion | Arm cloud CPUs | Graviton |
| Google-Wide Profiling (2010) | Fleet profiling paper | n/a |
| SMT / hyperthreading | Two hardware threads per core; contend at high utilisation | Graviton has no SMT |

## Interview line

> Traces tell me which request and which hop. Profiles tell me which function and line. Linked per span or per customer, I can say what was slow, for whom and why, and fix the 5-line bug instead of buying hardware.

## AWS mapping

- CodeGuru Profiler / Pyroscope
- Compute Optimizer; Karpenter on EKS; Graviton
- CUR 2.0 → Athena as wide events

## Practice question

**Q.** The cloud bill grew 40% in a quarter with flat traffic. Where do you look?

**Model answer.** Load the CUR into a queryable store and group by service, usage type and tag. Usual culprits: NAT/cross-AZ transfer, idle reserved capacity, oversized requests vs actual pod use, rollout artefacts, a hot loop. Then profile the top-cost services and fix the largest share first: 1% of 10% beats 5% of 1%.

## Exercise

Run pocs/09_cost_and_ci bin-packing; compute your own cluster's stranded cores.

## Takeaways

- Profiles complement traces
- Optimise the biggest consumers first
- Every billing dimension is an attribute
