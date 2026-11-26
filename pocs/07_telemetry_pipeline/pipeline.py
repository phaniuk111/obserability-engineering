"""POC 7: a telemetry pipeline (book ch16, ch27 tiers, ch7 PII defence in depth).

collect -> normalize -> secure (redact PII) -> enrich -> reduce -> route,
with bounded buffers, retries with exponential backoff + jitter, and
backpressure. Routing fans out to several destinations by rule, so adding a
tool is a config change, not reinstrumentation.
"""
from __future__ import annotations

import hashlib
import random
import re
from collections import deque
from dataclasses import dataclass, field
from typing import Callable

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
CARD = re.compile(r"\b(?:\d[ -]?){13,16}\b")
LOG_LINE = re.compile(r"^(?P<ts>\S+) (?P<level>[A-Z]+) (?P<msg>.*?)(?: (?P<kv>(?:\w[\w.]*=\S+ ?)+))?$")


def normalize(raw) -> dict:
    """Accept a dict (OTLP-ish) or a plaintext 'ts LEVEL msg k=v' line."""
    if isinstance(raw, dict):
        return dict(raw)
    m = LOG_LINE.match(raw.strip())
    if not m:
        return {"body": raw, "parse_error": True}
    ev = {"ts": m["ts"], "severity": m["level"].lower(), "body": m["msg"]}
    for pair in (m["kv"] or "").split():
        k, v = pair.split("=", 1)
        ev[k] = int(v) if v.isdigit() else v
    return ev


def stable_hash(value: str, salt: str = "pipeline-salt") -> str:
    """Stable, so the same user hashes the same everywhere (ch7: reversible via
    an internal lookup service, never by the vendor)."""
    return hashlib.sha256((salt + value).encode()).hexdigest()[:16]


def secure(ev: dict, hash_keys=("user.email", "user.id"), allow: set | None = None) -> dict:
    out = {}
    for k, v in ev.items():
        if allow is not None and k not in allow:
            continue
        if k in hash_keys and v is not None:
            out[k] = stable_hash(str(v))
        elif isinstance(v, str):
            out[k] = CARD.sub("[REDACTED_CARD]", EMAIL.sub("[REDACTED_EMAIL]", v))
        else:
            out[k] = v
    return out


def enricher(static: dict, lookups: dict[str, Callable] | None = None):
    def _enrich(ev: dict) -> dict:
        ev = {**static, **ev}
        for k, fn in (lookups or {}).items():
            ev[k] = fn(ev)
        return ev
    return _enrich


@dataclass
class Reducer:
    drop: Callable[[dict], bool] = lambda e: False
    drop_fields: tuple = ()
    dedupe_window: int = 1000
    _seen: deque = field(default_factory=deque)

    def __call__(self, ev: dict) -> dict | None:
        if self.drop(ev):
            return None
        for f in self.drop_fields:
            ev.pop(f, None)
        sig = (ev.get("body"), ev.get("service.name"), ev.get("severity"))
        if ev.get("severity") in ("debug", "info") and sig in self._seen:
            return None
        self._seen.append(sig)
        if len(self._seen) > self.dedupe_window:
            self._seen.popleft()
        return ev


class Destination:
    """Bounded queue + retry/backoff. Raises Backpressure when full."""

    def __init__(self, name, send: Callable[[list], None], capacity=1000, batch=100,
                 max_retries=5, base_delay=0.1, rng=random.Random(0)):
        self.name, self.send, self.capacity, self.batch = name, send, capacity, batch
        self.max_retries, self.base_delay, self.rng = max_retries, base_delay, rng
        self.queue: deque = deque()
        self.dropped = 0
        self.slept: list[float] = []

    def offer(self, ev) -> bool:
        if len(self.queue) >= self.capacity:
            self.dropped += 1
            return False  # caller sees backpressure
        self.queue.append(ev)
        return True

    def backoff(self, attempt: int) -> float:
        # full jitter: avoids synchronized retry storms (thundering herd)
        return self.rng.uniform(0, self.base_delay * 2 ** attempt)

    def flush(self, sleep=lambda s: None) -> int:
        sent = 0
        while self.queue:
            batch = [self.queue.popleft() for _ in range(min(self.batch, len(self.queue)))]
            for attempt in range(self.max_retries + 1):
                try:
                    self.send(batch)
                    sent += len(batch)
                    break
                except ConnectionError:
                    if attempt == self.max_retries:
                        self.queue.extendleft(reversed(batch))  # keep data, stop for now
                        return sent
                    d = self.backoff(attempt)
                    self.slept.append(d)
                    sleep(d)
        return sent


@dataclass
class Route:
    when: Callable[[dict], bool]
    to: Destination


class Pipeline:
    def __init__(self, stages: list[Callable], routes: list[Route]):
        self.stages, self.routes = stages, routes
        self.stats = {"in": 0, "dropped_by_reduce": 0, "routed": 0, "backpressure": 0}

    def process(self, raw) -> None:
        self.stats["in"] += 1
        ev = normalize(raw)
        for stage in self.stages:
            ev = stage(ev)
            if ev is None:
                self.stats["dropped_by_reduce"] += 1
                return
        for r in self.routes:
            if r.when(ev):
                if r.to.offer(ev):
                    self.stats["routed"] += 1
                else:
                    self.stats["backpressure"] += 1


# ------------------------------------------------------ tiered service levels
TIERS = {
    "high": {"traces": True, "tail_sample_rate": 10, "wide_events": True},   # critical path
    "medium": {"traces": True, "tail_sample_rate": 100, "wide_events": False},  # stable, customer facing
    "low": {"traces": False, "tail_sample_rate": None, "wide_events": False},  # health checks + synthetics
}


def tier_for(service: dict) -> str:
    if service.get("revenue") or service.get("active_development"):
        return "high"
    if service.get("customer_facing"):
        return "medium"
    return "low"
