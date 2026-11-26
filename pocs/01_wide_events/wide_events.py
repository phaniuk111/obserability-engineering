"""POC 1: wide events as the single source of truth (book ch1, ch5, ch6).

One flat, context-rich event per unit of work. Every "view" (metric, log
narrative, trace) is derived at read time, so you never have to know the
question in advance. Includes the average-of-averages trap from ch5.
"""
from __future__ import annotations

import math
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Iterable


Event = dict  # a wide event is just a flat dict of key -> scalar


# ---------------------------------------------------------------- emitting
@dataclass
class WideEvent:
    """Accumulate context during one unit of work, emit once at the end.

    This is the "canonical log line" pattern: add fields as you learn them,
    then send a single event. `main=True` marks it as the wide event (ch6).
    """

    name: str
    sink: list
    fields: dict = field(default_factory=dict)
    _start: float = field(default_factory=time.perf_counter)

    def add(self, **kv) -> "WideEvent":
        self.fields.update(kv)
        return self

    def time_block(self, label: str):
        """Context manager that records <label>.duration_ms on the main event
        (ch6: put key timings on the wide event instead of a child span)."""
        ev = self

        class _T:
            def __enter__(self):
                self.t = time.perf_counter()

            def __exit__(self, *exc):
                ev.fields[f"{label}.duration_ms"] = round((time.perf_counter() - self.t) * 1000, 3)

        return _T()

    def finish(self, error: Exception | None = None, slug: str | None = None) -> Event:
        ev = {"name": self.name, "main": True, **self.fields}
        ev["duration_ms"] = ev.get("duration_ms", round((time.perf_counter() - self._start) * 1000, 3))
        if error is not None:
            ev.update({"error": True, "exception.type": type(error).__name__,
                       "exception.message": str(error), "exception.slug": slug})
        else:
            ev.setdefault("error", False)
        self.sink.append(ev)
        return ev


# ---------------------------------------------------------------- querying
def where(events: Iterable[Event], pred: Callable[[Event], bool]) -> list[Event]:
    return [e for e in events if pred(e)]


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile (same idea as PERCENTILE_DISC)."""
    if not values:
        return math.nan
    s = sorted(values)
    k = max(0, math.ceil(p / 100 * len(s)) - 1)
    return s[k]


def group_by(events: Iterable[Event], *keys: str) -> dict[tuple, list[Event]]:
    out: dict[tuple, list[Event]] = defaultdict(list)
    for e in events:
        out[tuple(e.get(k) for k in keys)].append(e)
    return dict(out)


def aggregate(events: Iterable[Event], by: tuple[str, ...], field_: str, op: str = "p99") -> dict:
    """SELECT op(field) GROUP BY by -- computed at read time, any dimension."""
    res = {}
    for key, evs in group_by(events, *by).items():
        vals = [e[field_] for e in evs if e.get(field_) is not None]
        if op == "count":
            res[key] = len(evs)
        elif op == "avg":
            res[key] = sum(vals) / len(vals) if vals else math.nan
        elif op.startswith("p"):
            res[key] = percentile(vals, float(op[1:]))
        elif op == "sum":
            res[key] = sum(vals)
        else:
            raise ValueError(op)
    return res


def time_buckets(events: Iterable[Event], width_s: int, field_: str, op: str = "p99") -> dict[int, float]:
    """Derive a metric time series from events (ch5: P99 per minute)."""
    tagged = [dict(e, _bucket=int(e["ts"] // width_s) * width_s) for e in events]
    return {k[0]: v for k, v in sorted(aggregate(tagged, ("_bucket",), field_, op).items())}


def narrative(events: Iterable[Event], *cols: str) -> list[tuple]:
    """Derive a log-like narrative (ch5)."""
    return [tuple(e.get(c) for c in cols) for e in sorted(events, key=lambda e: e.get("ts", 0))]


# ------------------------------------------------- average of averages trap
def naive_avg_of_avgs(per_instance_avg: dict[str, float]) -> float:
    return sum(per_instance_avg.values()) / len(per_instance_avg)


def weighted_avg(counts: dict[str, int], totals_ms: dict[str, float]) -> float:
    """What a histogram (count + sum) lets you compute correctly."""
    return sum(totals_ms.values()) / sum(counts.values())


# ---------------------------------------------------------------- demo data
def synthetic_checkout_events(n: int = 5000, seed: int = 7) -> list[Event]:
    """Checkout traffic where one cohort (build b_4471 + flag on + ap-southeast-2)
    is slow. Aggregate P99 barely moves; slicing finds it immediately."""
    rng = random.Random(seed)
    events = []
    for i in range(n):
        region = rng.choice(["us-east-1", "eu-west-1", "ap-southeast-2"])
        build = rng.choice(["b_4470", "b_4471"])
        flag = rng.random() < 0.3
        plan = rng.choice(["free", "pro", "enterprise"])
        dur = rng.lognormvariate(4.3, 0.35)  # ~75ms median
        if build == "b_4471" and flag and region == "ap-southeast-2":
            dur *= 6
        events.append({
            "ts": 1_700_000_000 + i * 0.5, "name": "checkout", "main": True,
            "service.name": "checkout-api", "http.route": "/checkout", "http.request.method": "POST",
            "cloud.region": region, "deploy.build_id": build, "feature_flag.new_checkout": flag,
            "user.plan": plan, "user.id": f"u_{rng.randint(1, 900)}", "duration_ms": round(dur, 2),
            "error": rng.random() < 0.004,
        })
    return events


if __name__ == "__main__":
    evs = synthetic_checkout_events()
    print("overall p99:", round(percentile([e["duration_ms"] for e in evs], 99), 1))
    worst = sorted(aggregate(evs, ("deploy.build_id", "feature_flag.new_checkout", "cloud.region"),
                             "duration_ms", "p99").items(), key=lambda kv: -kv[1])[:3]
    for k, v in worst:
        print("p99", k, round(v, 1))
    print("naive avg of avgs:", round(naive_avg_of_avgs({"web.1": 120, "web.2": 230, "web.3": 200}), 1))
    print("weighted:", round(weighted_avg({"web.1": 100, "web.2": 57, "web.3": 98},
                                          {"web.1": 12000, "web.2": 13110, "web.3": 19600}), 1))
