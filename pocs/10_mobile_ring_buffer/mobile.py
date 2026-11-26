"""POC 10: mobile observability with local storage + a remote control plane
(book ch19, Matt Klein's section), and a user-focused SLI (Hanson Ho's section).

Devices log everything into a bounded ring buffer that never leaves the
device by default. The server pushes small finite-state-machine rules; when a
rule matches, the device increments a counter and/or uploads the buffer
("session replay"). Plus: checkout completion rate as intention -> outcome.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


class RingBuffer:
    """Fixed-size buffer; oldest events fall off. (On device: persisted to
    disk off the main thread so it survives process death.)"""

    def __init__(self, capacity: int):
        self.buf: deque = deque(maxlen=capacity)

    def log(self, event: dict):
        self.buf.append(event)

    def dump(self) -> list[dict]:
        return list(self.buf)


@dataclass
class Rule:
    """FSM pushed from the server, e.g. 'user views checkout; if they leave or
    15 s pass without checkout_complete, count it and dump the session'."""
    rule_id: str
    start: str
    success: str
    abandon_events: tuple[str, ...]
    timeout_s: float
    upload_on_abandon: bool = True
    match: dict = field(default_factory=dict)  # cohort targeting e.g. {"app_version": "3.2.8"}


class Device:
    def __init__(self, device_ctx: dict, capacity: int = 500):
        self.ctx = device_ctx
        self.buffer = RingBuffer(capacity)
        self.rules: list[Rule] = []
        self.state: dict[str, float] = {}  # rule_id -> start ts
        self.counters: dict[str, int] = {}
        self.uploads: list[dict] = []

    def apply_config(self, rules: list[Rule]):  # control plane push, no app release needed
        self.rules = [r for r in rules if all(self.ctx.get(k) == v for k, v in r.match.items())]

    def _fire(self, rule: Rule, ts: float, reason: str):
        self.counters[rule.rule_id] = self.counters.get(rule.rule_id, 0) + 1
        if rule.upload_on_abandon:
            self.uploads.append({"rule_id": rule.rule_id, "reason": reason, "ts": ts, **self.ctx,
                                 "session": self.buffer.dump()})
        self.state.pop(rule.rule_id, None)

    def log(self, name: str, ts: float, **attrs):
        self.buffer.log({"name": name, "ts": ts, **attrs})
        for r in self.rules:
            started = self.state.get(r.rule_id)
            if started is not None and ts - started > r.timeout_s:
                self._fire(r, ts, "timeout")
                started = None
            if name == r.start and started is None:
                self.state[r.rule_id] = ts
            elif started is not None and name == r.success:
                self.state.pop(r.rule_id, None)
            elif started is not None and name in r.abandon_events:
                self._fire(r, ts, f"abandon:{name}")


def completion_rate(events: list[dict], start: str = "start_checkout", end: str = "end_checkout",
                    by: str | None = None) -> dict:
    """Intention -> outcome. Join start/end on checkout_id; group by any context."""
    starts = {e["checkout_id"]: e for e in events if e["name"] == start}
    done = {e["checkout_id"] for e in events if e["name"] == end}
    groups: dict = {}
    for cid, e in starts.items():
        k = e.get(by) if by else "all"
        s, d = groups.get(k, (0, 0))
        groups[k] = (s + 1, d + (cid in done))
    return {k: round(d / s, 3) for k, (s, d) in groups.items()}
