"""POC 9: performance, cost and CI arithmetic you get asked about (book ch18, ch20, ch24, ch29).

- Kubernetes bin-packing waste (20-vCPU pods on 32- vs 64-core nodes).
- Cloud cost-and-usage rows as wide events; group by any tag.
- CI retries: P50 barely moves, P90 doubles; flake rate as an SLI.
- Amdahl's law for build parallelism.
- Build-vs-buy fully loaded cost (the "free" ELK example).
- Rough per-request serverless cost from span duration.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict


def pods_per_node(node_vcpu: int, pod_vcpu: float, daemonset_vcpu: float = 1.0) -> tuple[int, float]:
    usable = node_vcpu - daemonset_vcpu
    n = int(usable // pod_vcpu)
    return n, usable - n * pod_vcpu  # (pods, stranded vCPU)


def cost_by(rows: list[dict], *keys: str, field: str = "cost_usd") -> dict[tuple, float]:
    out: dict[tuple, float] = defaultdict(float)
    for r in rows:
        out[tuple(r.get(k) for k in keys)] += r[field]
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def pct(values: list[float], p: float) -> float:
    s = sorted(values)
    return s[max(0, math.ceil(p / 100 * len(s)) - 1)]


def simulate_ci(n_runs: int, base_min: float, flake_rate: float, retries: int, seed: int = 0) -> dict:
    rng = random.Random(seed)
    durations, failed, retried = [], 0, 0
    for _ in range(n_runs):
        t, attempts = 0.0, 0
        while True:
            attempts += 1
            t += base_min * rng.uniform(0.9, 1.1)
            if rng.random() >= flake_rate:
                break
            if attempts > retries:
                failed += 1
                break
        retried += attempts > 1
        durations.append(t)
    return {"p50": pct(durations, 50), "p90": pct(durations, 90), "p99": pct(durations, 99),
            "failure_rate": failed / n_runs, "flake_rate_observed": retried / n_runs}


def amdahl_speedup(parallel_fraction: float, workers: int) -> float:
    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)


def fully_loaded_build_cost(hardware_per_month: float, engineers: int, salary: float,
                            recruiting_pct: float = 0.25) -> dict:
    yearly = hardware_per_month * 12 + engineers * salary
    first_year = yearly + engineers * salary * recruiting_pct
    return {"yearly_run_rate": yearly, "first_year": first_year}


def serverless_request_cost(duration_ms: float, memory_gb: float, price_per_gb_s: float,
                            per_request: float = 0.0) -> float:
    """Span duration converts straight into cost: put it on the span as an attribute."""
    return duration_ms / 1000 * memory_gb * price_per_gb_s + per_request
