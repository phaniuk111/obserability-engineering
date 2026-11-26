"""POC 5: cheap and accurate enough sampling (book ch4, ch15).

- Record the sample rate on every kept event and reconstruct with weights.
- Weighted percentile (the {1,5},{3,2},{7,9} median example).
- Consistent (deterministic) sampling from the trace ID so traces stay whole.
- Per-key target-rate dynamic sampler (the dynsampler idea).
- Tail sampling of a buffered trace.
"""
from __future__ import annotations

import hashlib
import random
from collections import Counter, defaultdict
from typing import Callable, Iterable


# ------------------------------------------------------------ reconstruct
def weighted_count(kept: Iterable[dict], pred: Callable[[dict], bool] = lambda e: True) -> float:
    return sum(e["sample_rate"] for e in kept if pred(e))


def weighted_sum(kept: Iterable[dict], field: str) -> float:
    return sum(e[field] * e["sample_rate"] for e in kept)


def weighted_percentile(pairs: list[tuple[float, float]], p: float) -> float:
    """pairs = [(value, sample_rate)]: expand by weight without materialising."""
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    target = p / 100 * total
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= target:
            return v
    return pairs[-1][0]


# ------------------------------------------------------------- consistent
def trace_threshold(trace_id: str) -> float:
    """Map a trace ID to a stable number in [0,1). Every service computes the
    same value, so with rate N they all keep or all drop the same trace."""
    h = hashlib.sha256(trace_id.encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64


def keep_consistent(trace_id: str, sample_rate: float) -> bool:
    return trace_threshold(trace_id) < 1.0 / sample_rate


# ------------------------------------------------------ fixed-rate sampler
class FixedRateSampler:
    def __init__(self, rate: int, rng: random.Random | None = None):
        self.rate, self.rng = rate, rng or random.Random(0)

    def sample(self, event: dict) -> dict | None:
        if self.rng.random() < 1 / self.rate:
            return {**event, "sample_rate": self.rate}
        return None


# ------------------------------------------- per-key target-rate sampler
class KeyedTargetRateSampler:
    """Each interval, give every key a fair share of `target_per_interval` kept
    events. Rare keys (errors, new customers) keep everything; noisy keys are
    sampled harder. Rates recompute from the previous interval's counts."""

    def __init__(self, key_fn: Callable[[dict], tuple], target_per_interval: int,
                 never: Callable[[dict], bool] = lambda e: False, rng: random.Random | None = None):
        self.key_fn, self.target, self.never = key_fn, target_per_interval, never
        self.rng = rng or random.Random(0)
        self.counts: Counter = Counter()
        self.rates: dict[tuple, float] = defaultdict(lambda: 1.0)

    def rollover(self) -> None:
        if self.counts:
            share = self.target / len(self.counts)
            self.rates = defaultdict(lambda: 1.0, {k: max(1.0, n / share) for k, n in self.counts.items()})
        self.counts = Counter()

    def sample(self, event: dict) -> dict | None:
        if self.never(event):
            return None
        k = self.key_fn(event)
        self.counts[k] += 1
        rate = self.rates[k]
        if self.rng.random() < 1 / rate:
            return {**event, "sample_rate": rate}
        return None


# ----------------------------------------------------------- tail sampling
def tail_sample(trace: list[dict], base_rate: int, slow_ms: float = 500) -> tuple[bool, int]:
    """Decide on the whole buffered trace: keep anything with an error or a slow
    root; otherwise keep 1/base_rate consistently by trace id."""
    root = next(s for s in trace if s.get("trace.parent_id") is None)
    if any(s.get("error") for s in trace) or root["duration_ms"] > slow_ms:
        return True, 1
    return keep_consistent(root["trace.trace_id"], base_rate), base_rate
